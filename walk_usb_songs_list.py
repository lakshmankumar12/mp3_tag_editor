#!/usr/bin/python

from __future__ import print_function
import os
import sys
import find_tags_of_files
import json
import collections
from fuzzywuzzy import fuzz,process

def get_mp3_songs_info(root_path, max_file, use_v1_on_absent_v2):
    '''
        walk the root_path and scans all mp3 files in it.
        Prepares a dict of full_path -> (basename,path,title,album,artist,alb-artist)
        Also returns the non mp3 files in (non_mp3)
        Also returns bad mp3 files in (bad_mp3)

        Internal function. Used dump_mp3_songs_info() the wrapper
    '''
    non_mp3=[]
    bad_mp3=[]
    mp3_files={}
    max_lens = {}
    max_lens["FileName"] = 0
    count = 0
    for subdir, dirs, files in os.walk(root_path, followlinks=True):
        if count > max_file:
            break
        for i in files:
            if count > max_file:
                break
            filename = os.path.join(subdir,i)
            if not i.endswith('.mp3'):
                non_mp3.append(filename)
                continue
            (ok,tags) = find_tags_of_files.grab_tags_of_file(max_lens, filename)
            if not ok:
                bad_mp3.append(filename)
                continue
            file_info = {}
            file_info['basename'] = i
            file_info['pathname'] = subdir
            for tag in ['TIT2','TALB','TPE1','TPE2']:
                if tag in tags:
                    file_info[tag] = tags[tag]
            if use_v1_on_absent_v2:
                if not 'TIT2' in tags and 'V1-Title' in tags:
                    file_info['TIT2'] = tags['V1-Title']
                if not 'TALB' in tags and 'V1-Album' in tags:
                    file_info['TALB'] = tags['V1-Album']
                if not 'TPE1' in tags and not 'TPE2' in tags and 'V1-Artist' in tags:
                    file_info['TPE1'] = tags['V1-Artist']
            mp3_files[filename] = file_info
            count += 1
    return mp3_files,bad_mp3,non_mp3

def dump_mp3_songs_info(root_path, json_path, json_prefix, max_file=100, use_v1_on_absent_v2=False):
    '''
        Given a root-path, json-path/prefix, it dumps all mp3-files in root-path
        as a json file in json file. You should find 3 files - good, bad, non

        The good file has a dict of (path->(tags of the song))
    '''
    (good,bad,non) = get_mp3_songs_info(root_path, max_file, use_v1_on_absent_v2)
    goodfile = os.path.join(json_path, json_prefix+'good.json')
    badfile = os.path.join(json_path, json_prefix+'bad.json')
    nonfile = os.path.join(json_path, json_prefix+'non.json')
    for ob,filename in [ (good, goodfile), (bad, badfile) , (non, nonfile) ]:
        with open(filename,'w') as fd:
            json.dump(ob,fd,indent=4)

def load_good_file_info(json_file, dump_result=None):
    '''
        This is just a helper function. You dont have to call it directly.

        When given a json/dict of "path": (basenames, titles, albums) .. it gives
        a grander dict, with keys:
            full_json -> the input json
            basename  -> dict of basenames to all paths that have this basename
            TIT2      -> ...    titles
            TALB      -> ...    titles
            TPE1      -> ...    titles
            TPE2      -> ...    titles
    '''
    with open(json_file, 'r') as fd:
        good = json.load(fd)
    basenames = collections.defaultdict(list)
    titles = collections.defaultdict(list)
    albums = collections.defaultdict(list)
    artists = collections.defaultdict(list)
    albartists = collections.defaultdict(list)
    namesAndDict = [ ('basename', basenames) , ( 'TIT2', titles), ('TALB', albums) , ('TPE1', artists), ('TPE2', albartists) ]
    for name, dt in namesAndDict:
        for i in good:
            if name in good[i]:
                dt[good[i][name]].append(i)
    info = {}
    info['full_json'] = good
    for name, dt in namesAndDict:
        info[name] = dt
    if dump_result:
        with open(dump_result,'w') as fd:
            json.dump(info,fd,indent=4)
    return info

def compare_lists(reference_file, check_file):
    '''
        You should supply as input the good-file prepared by dump_mp3_songs_info()

        It then calls load_good_file_info() to prepare the curated data-structure.
        Takes each entry in the check_dict and tries to get a best match from good-dict.

        If an unambiguous match is found its kept in unambigous (check-path --> good-path)
        In no matches are found , its kept in        nomatches  (check-path)
        If ambiguos matches are foudn, its kept in   ambiguous  (check-path -> [ .. potential good-paths.. ])

        Its recommended to do a verify_matches() after this

        How matching is done:
            * extracts basename matches
            * extracts title matches
            * extracts album matches
            * adds each match in a dict of path->count.
            * The max-count is taken if that's unambiguous otherwise gives up
    '''
    reference_info = load_good_file_info(reference_file)
    check_info = load_good_file_info(check_file)
    check_full_json = check_info['full_json']
    all_reference_basenames = reference_info['basename'].keys()
    all_reference_titles = reference_info['TIT2'].keys()
    all_reference_albums = reference_info['TALB'].keys()
    found = {}
    not_found = []
    count = 0
    for check_full_path in check_full_json:
        # if count >= 1:
            # return (found,not_found)
        count += 1
        curr_check_file = check_full_json[check_full_path]
        basename = curr_check_file['basename']
        title = None
        album = None
        if 'TIT2' in curr_check_file:
            title = curr_check_file['TIT2']
        if 'TALB' in curr_check_file:
            album = curr_check_file['TALB']
        basename_results = process.extract(basename, all_reference_basenames)
        title_results = process.extract(title, all_reference_titles)
        albums_results = process.extract(album, all_reference_albums)
        #print("Debug .. {} Got results: basename:\n{}\ntitle_results:\n{}\nalbum_results:\n{}\n".format(check_full_path,basename_results,title_results,albums_results))
        basename_results = [ i[0] for i in basename_results if i[1] > 70 ]
        title_results = [ i[0] for i in title_results if i[1] > 70 ]
        albums_results = [ i[0] for i in albums_results if i[1] > 70 ]
        #print("Debug .. {} Got stripped results: basename:\n{}\ntitle_results:\n{}\nalbum_results:\n{}\n".format(check_full_path,basename_results,title_results,albums_results))
        all_paths = collections.defaultdict(int)
        for i in basename_results:
            for path in reference_info['basename'][i]:
                #print("Debug .. {} Adding {} due to basename {}".format(check_full_path,path,i))
                all_paths[path] += 1
        for i in title_results:
            for path in reference_info['TIT2'][i]:
                #print("Debug .. {} Adding {} due to title {}".format(check_full_path,path,i))
                all_paths[path] += 1
        for i in albums_results:
            for path in reference_info['TALB'][i]:
                #print("Debug .. {} Adding {} due to album {}".format(check_full_path,path,i))
                all_paths[path] += 1
        #print("Debug .. {} all_paths:\n{}\n".format(check_full_path, all_paths))
        max_occurance = max(all_paths.values())
        max_keys = [ k for k in all_paths if all_paths[k] == max_occurance]
        #print("Debug .. {} max_keys:\n{}\n".format(check_full_path, max_keys))
        if len(max_keys) == 1:
            print("{}. found {} matched to {}".format(count, check_full_path,max_keys[0]))
            found[check_full_path] = max_keys[0]
        else:
            print("{}. cound't match {}".format(count, check_full_path))
            not_found.append(check_full_path)
    return (found,not_found)

def prepare_reference_work_info(reference_file):
    '''
    Take a good-info json file and prepares all working dicts
    to be used later by get_matching_entry
    '''
    reference_info = load_good_file_info(reference_file)
    ref=lambda: None
    setattr(ref,'info', reference_info)
    setattr(ref,'basenames', reference_info['basename'].keys())
    setattr(ref,'titles', reference_info['TIT2'].keys())
    setattr(ref,'albums', reference_info['TALB'].keys())
    setattr(ref,'artists', reference_info['TPE1'].keys())
    setattr(ref,'albartists', reference_info['TPE2'].keys())
    return ref


def get_matching_entry(ref, title, album, artist=None, albArtist=None, basename=None):
    def work_on_entry(final, toLook, refList, refMainDict):
        if toLook:
            results = process.extract(toLook,refList)
            results = [ i[0] for i in results if i[1] > 70 ]
            for i in results:
                for path in refMainDict[i]:
                    final[path] += 1
        return None
    final = collections.defaultdict(int)
    work_on_entry(final, title, ref.titles, ref.info['TIT2'])
    work_on_entry(final, album, ref.albums, ref.info['TALB'])
    if artist:
        work_on_entry(final, artist, ref.artists, ref.info['TPE1'])
    if albArtist:
        work_on_entry(final, albArtist, ref.albartists, ref.info['TPE2'])
    if basename:
        work_on_entry(final, basename, ref.basenames, ref.info['basename'])
    max_occurance = max(final.values())
    max_keys = [ k for k in final if final[k] == max_occurance]
    if len(max_keys) == 1:
        return max_keys[0]
    else:
        return None

def verify_matches(reference_json, check_json, matches):
    '''
        Takes the full_json of reference and check and match
        For each match having a mapping from check->reference,
        it categories that under (a match if ration is >90)
           all_match (title, album, artist, alb-artist)
           three_match
           two_match
           one_match
           zero_match
           fishy (any ration less than 70)
        Note that ration values between 71->90 are neither considered fishy nor match
    '''
    result = {}
    result['all_match'] = {}
    result['three_match'] = {}
    result['two_match'] = {}
    result['one_match'] = {}
    result['zero_match'] = {}
    result['something_fishy'] = {}
    for i in matches:
        r = reference_json[matches[i]]
        c = check_json[i]
        #print ("reference:{}".format(json.dumps(r,indent=4)))
        #print ("check:{}".format(json.dumps(r,indent=4)))
        basename_ratio = fuzz.ratio(r['basename'],c['basename'])
        #print ("basename_ratio:{}".format(basename_ratio))
        fields = ['TIT2', 'TALB', 'TPE1', 'TPE2']
        ratios = [None]*len(fields)
        for n,f in enumerate(fields[:2]):
            if f in c:
                ratios[n] = fuzz.ratio(r[f],c[f])
        if 'TPE2' in c and 'TPE1' in c:
            for n,f in enumerate(fields[2:],2):
                ratios[n] = fuzz.ratio(r[f],c[f])
        elif 'TPE1' in c and 'TPE1' in r:
            ratios[2] = fuzz.ratio(r['TPE1'],c['TPE1'])
            if 'TPE2' in r:
                ratios[2] = max (ratios[2], fuzz.ratio(r['TPE2'],c['TPE1']))
        res = {}
        res['Match'] = matches[i]
        res['Ratios'] = ratios
        count = 0
        fishy = 0
        for j in ratios:
            if j:
                if j > 90:
                    count+=1
                if j < 70:
                    fishy=1
        where = 'zero_match'
        if fishy:
            where = 'something_fishy'
        elif count == 4:
            where = 'all_match'
        elif count == 3:
            where = 'three_match'
        elif count == 2:
            where = 'two_match'
        elif count == 1:
            where = 'one_match'
        result[where][i] = res
    return result

def findSongsInMyCollection(reference_file, matched_store, toCheck):
    '''
        reference_file : the good-file prepared by dump_mp3_songs_info()
        matched_store  : json file having already mapped results
        toCheck        : json containing list of [{'TIT2','TALB'}] dicts

        returns (found/notfound) containing ({'TIT2','TALB'},path)
                        path is a single result in found
                             and a list(empty too) in not-found
    '''
    with open(matched_store,'r') as fd:
        matched_store_info = json.load(fd)
    reference_info = load_good_file_info(reference_file)
    all_reference_titles = reference_info['TIT2'].keys()
    all_reference_albums = reference_info['TALB'].keys()
    found = []
    notfound = []
    count = 0
    for track in toCheck:
        count += 1
        title = track['TIT2']
        album = track['TALB']
        if album in matched_store_info:
            if title in matched_store_info[album]:
                print ("{}. {}, {} is already matched".format(count, title, album))
                continue
        title_results = process.extract(title, all_reference_titles)
        albums_results = process.extract(album, all_reference_albums)

        title_results = [ i[0] for i in title_results if i[1] > 80 ]
        albums_results = [ i[0] for i in albums_results if i[1] > 80 ]

        all_paths = collections.defaultdict(int)
        for i in title_results:
            for path in reference_info['TIT2'][i]:
                all_paths[path] += 1
        for i in albums_results:
            for path in reference_info['TALB'][i]:
                all_paths[path] += 1

        if not all_paths:
            notfound.append((track, []))
            continue

        max_occurance = max(all_paths.values())
        max_keys = [ k for k in all_paths if all_paths[k] == max_occurance]

        if len(max_keys) == 1:
            print("{}. {},{} matched to {}".format(count, title, album, max_keys[0]))
            found.append((track,max_keys[0]))
        else:
            print("{}. {},{} didn't to {}".format(count, title, album, max_keys[0]))
            notfound.append((track, max_keys))
    return found,notfound

def writeFoundNotFoundListsToFile(f,nf,foundFileName,notFoundFileName):
    foundReOrged = {}
    for track in f:
        a = track[0]['TALB']
        t = track[0]['TIT2']
        if a not in foundReOrged:
            foundReOrged[a] = {}
        foundReOrged[a][t] = track[1]
    notFoundReorged = {}
    for track in nf:
        a = track[0]['TALB']
        t = track[0]['TIT2']
        if a not in notFoundReorged:
            notFoundReorged[a] = {}
        notFoundReorged[a][t] = track[1]
    with open(foundFileName,'w') as fd:
        json.dump(foundReOrged,fd,indent=4)
    with open(notFoundFileName,'w') as fd:
        json.dump(notFoundReorged,fd,indent=4)


if __name__ == '__main__':
    main()


""" blocks.py

Output one shapefile per MSA featuring all the blocks it contains
"""
import os
import csv
import fiona


#
# Import MSA to blockgroup crosswalk 
#
msa_to_block = {}
with open('data/crosswalks/msa_blocks.csv', 'r') as source:
    reader = csv.reader(source, delimiter='\t')
    reader.next()
    for rows in reader:
        msa = rows[0]
        block = rows[1]
        if msa not in msa_to_block:
            msa_to_block[msa] = []
        msa_to_block[msa].append(block)



#
# Perform the extraction
#
for n,msa in enumerate(msa_to_block):
    print "Extract blocks for %s (%s/%s)"%(msa,
                                        n+1,
                                        len(msa_to_block))
    states = list(set([b[:2] for b in msa_to_block[msa]]))

    ## Get all blockgroups
    all_block = {}
    for st in states:
        with fiona.open('data/shp/state/%s/blocks.shp'%st, 'r',
                'ESRI Shapefile') as source:
            source_crs = source.crs
            for f in source:
                all_block[f['properties']['BLKIDFP00']] = f['geometry']

    ## blockgroups within cbsa
    msa_block = {block: all_block[block] for block in msa_to_block[msa]}

    ## Save
    if not os.path.isdir('data/shp/msa/%s'%msa):
        os.mkdir('data/shp/msa/%s'%msa)

    schema = {'geometry': 'Polygon',
              'properties': {'BLKIDFP00': 'str'}}
    with fiona.open('data/shp/msa/%s/blocks.shp'%msa, 'w', 
            'ESRI Shapefile',
            crs = source_crs,
            schema = schema) as output:
        for block in msa_block:
            rec = {'geometry':msa_block[block], 'properties':{'BLKIDFP00':block}}
            output.write(rec)

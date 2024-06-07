
import argparse
import codecs
import csv
import fnmatch
import html
import json
import os
import re



def get_review_filesnames(input_dir):
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in fnmatch.filter(filenames, '*.html'):
            yield os.path.join(root, filename)


hotelnamere = re.compile(r'"description" content="(.*?): ')
block = re.compile(r'"reviewBody":(.*?)"priceRange"')
rating_block = re.compile(r'ratingValue":"(.*?)"},')

address_block = re.compile(r'"PostalAddress",(.*?)"addressCountry"')
date_block = re.compile(r' >Reviewed (.*?) </span>')


def main():
    parser = argparse.ArgumentParser(
        description='TripAdvisor Hotel parser')
    parser.add_argument('-d', '--dir', help='Directory with the data for parsing', required=True)
    parser.add_argument('-o', '--outfile', help='Output file path for saving the reviews in csv format', required=True)

    args = parser.parse_args()


    with codecs.open(args.outfile, 'w', encoding='utf8') as out:
        writer = csv.writer(out, lineterminator='\n')
        for filepath in get_review_filesnames(args.dir):
            with codecs.open(filepath, mode='r', encoding='utf8') as file:
                htmlpage = file.read()
            print(filepath)
            hotelname = hotelnamere.findall(htmlpage)[0]

            try:
                reviewtext = block.findall(htmlpage)[0].split('","',1)[0]
                overallrating = int(rating_block.findall(block.findall(htmlpage)[0].split('","',1)[1])[0])
                
                # new additions
                date_stamp = date_block.findall(htmlpage)[0]
                address_vals = re.split(':|,',address_block.findall(htmlpage)[0].replace('"',''))
                address_dict = dict(zip(address_vals[::2], address_vals[1::2])) 
            except IndexError:
                continue
            
            try:
                address = address_dict['streetAddress']
                locality = address_dict['addressLocality'],
                region = address_dict['addressRegion']
                postal_code = address_dict['postalCode']
            except KeyError:
                continue

            if overallrating >= 4:
                binaryrating = 'positive'
            else:
                binaryrating = 'negative'

            try:
                
                review = [filepath, hotelname, reviewtext, overallrating, binaryrating, date_stamp, address, locality, region, postal_code]

                writer.writerow(review)
            except KeyError:
                continue



if __name__ == '__main__':
    main()

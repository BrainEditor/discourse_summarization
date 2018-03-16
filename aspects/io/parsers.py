import gzip
import json
import pickle
from collections import defaultdict

import simplejson
from tqdm import tqdm

from aspects.utilities import settings


def parse_reviews(path):
    with gzip.open(path, 'rb') as g:
        for l in g:
            yield eval(l)


def amazon_dataset_parse(dataset_path, column='reviewText', n_reviews=100000):
    i = 0
    reviews = {}
    for d in tqdm(parse_reviews(dataset_path)):
        reviews[i] = d[column]
        i += 1
        if i > n_reviews:
            break
    with open(dataset_path.replace('.gz', ''), 'wb') as j:
        json.dump(reviews, j)


def conceptnet_io_parse(langs={u'en'}):
    with gzip.open(settings.CONCEPTNET_IO_PATH_GZ.as_posix(), 'rb') as conceptnet_io_file:
        conceptnet_relations = defaultdict(list)
        for line in tqdm(conceptnet_io_file):
            relation_elements = line.split('\t')
            concept_start = relation_elements[2].split('/')[3].decode('utf8')
            concept_end = relation_elements[3].split('/')[3].decode('utf8')
            start_lang = relation_elements[2].split('/')[2].decode('utf8')
            end_lang = relation_elements[3].split('/')[2].decode('utf8')
            if start_lang in langs and end_lang in langs:
                concept_relation = {
                    'start': concept_start,
                    'start-lang': start_lang,
                    'end': concept_end,
                    'end-lang': end_lang,
                    'weight': float(simplejson.loads(relation_elements[4])['weight']),
                    'relation': relation_elements[1].split('/')[2].decode('utf8')
                }
                # it will be easier to look up by aspects
                conceptnet_relations[concept_start].append(concept_relation)
                conceptnet_relations[concept_end].append(concept_relation)
    with open(settings.CONCEPTNET_IO_PKL.as_posix(), 'wb') as conceptnet_io_file:
        pickle.dump(conceptnet_relations, conceptnet_io_file)


if __name__ == '__main__':
    amazon_dataset_parse(settings.AMAZON_REVIEWS_APPS_FOR_ANDROID_DATASET_GZ.as_posix())
    amazon_dataset_parse(settings.AMAZON_REVIEWS_CELL_PHONES_AND_ACCESSORIES_DATASET_GZ.as_posix())
    amazon_dataset_parse(settings.AMAZON_REVIEWS_AMAZON_INSTANT_VIDEO_DATASET_GZ.as_posix())
    conceptnet_io_parse()

import numpy as np
import json
from unidecode import unidecode
from mongomock import MongoClient

# NOTE: you MUST change this cell
# New methods / functions must be written under class Solution.
class Solution:
    def __init__(self):
        # list provice, district, ward for private test, do not change for any reason
        self.province_path = 'list_province.txt'
        self.district_path = 'list_district.txt'
        self.ward_path = 'list_ward.txt'

        # write your preprocess here, add more method if needed
        self.client = MongoClient()
        self.address_classification = self.client.address_classification
        self.province_db = self.address_classification.province
        self.district_db = self.address_classification.district
        self.ward_db = self.address_classification.ward

        with open('data/tinh_tp.json', 'r') as file:
            data = json.load(file)
        for document in data.values():
            self.province_db.insert_one(document)
        
        with open('data/quan_huyen.json', 'r') as file:
            data = json.load(file)
        for document in data.values():
            self.district_db.insert_one(document)

        with open('data/xa_phuong.json', 'r') as file:
            data = json.load(file)
        for document in data.values():
            self.ward_db.insert_one(document)
        # Load the provinces
        self.provinces = self.get_provinces()

    def levenshtein_distance(self, word1: str, word2: str):
        """Calculate the levenshtein distance between two strings.

        Args:
            word1 (str): string from input text. 
                Should be string without blankspace between words, without diacritical marks.
                For example: 'TP. Hồ Chí Minh' should be 'tphochiminh'.
            word2 (str): string from predefined dataset.

        Returns:
            int: an integer value represents the distance.
                The smaller the value, the more similar the two strings are.
                In the best case, distance=0 indicates that two strings are identical.
        """
        # word1 as the row
        size_row = len(word1) + 1
        # word2 as the column
        size_col = len(word2) + 1
        # Initiate matrix of zeros
        distances = np.zeros((size_row, size_col), dtype=int)

        for x in range(size_row):
            distances[x][0] = x
        for y in range(size_col):
            distances[0][y] = y
        
        for x in range(1, size_row):
            for y in range(1, size_col):
                if word1[x-1] == word2[y-1]:
                    distances[x][y] = distances[x-1][y-1]
                else:
                    distances[x][y] = min(
                        distances[x-1][y]+1,
                        distances[x-1][y-1]+1,
                        distances[x][y-1]+1
                    )
        return distances[size_row-1][size_col-1]

    def find_min_distance(self, distances: dict):
        # Input a dict of distance and province code
        # for example, distances = {'01': 0.5, '02': 1}
        # output the province code
        return min(distances, key=distances.get)
    
    def split_input(self, s: str):
        try:
            if ',' in s:
                text = s.split(',')
                if len(text) >= 3:
                    province = text[-1]
                    district = text[-2]
                    ward = text[-3]
                else:
                    if len(text[-1]) > 17:
                        province = s[-11:]
                    else:
                        province = text[-1]
                    district = s[:-len(province)]
                    ward = s[:-len(province)]
            else:
                province = s[-11:]
                district = s[-31:-11]
                ward = s[:-31]
        except:
            pass
        province = unidecode(province).lower().replace(' ', '')
        district = unidecode(district).lower().replace(' ', '')
        ward = unidecode(ward).lower().replace(' ', '')
        return province, district, ward

    def get_provinces(self):
        provinces = []
        result = self.province_db.find({}, {'slug': True, 'code': True})
        for province in result:
            provinces.append(province)
        return provinces

    def get_districts(self, province_code):
        districts = []
        if province_code:
            result = self.district_db.find({'parent_code': province_code}, {'slug': True, 'code': True, 'parent_code': True})
        else:
            result = self.district_db.find({}, {'slug': True, 'code': True, 'parent_code': True})
        for district in result:
            districts.append(district)
        return districts

    def get_wards(self, district_code):
        wards = []
        if district_code:
            result = self.ward_db.find({'parent_code': district_code}, {'slug': True, 'code': True, 'parent_code': True})
        else:
            result = self.ward_db.find({}, {'slug': True, 'code': True, 'parent_code': True})
        for ward in result:
            wards.append(ward)
        return wards
    
    def get_matched_province(self, province_code):
        return self.province_db.find_one({'code': province_code})['name']

    def get_matched_district(self, district_code):
        return self.district_db.find_one({'code': district_code})['name']

    def get_matched_ward(self, ward_code):
        return self.ward_db.find_one({'code': ward_code})['name']

    def process(self, s: str):
        # write your process string here
        # Pre-processing the input string here
        input_province, input_district, input_ward = self.split_input(s)

        # Find the province
        if input_province:
            all_province_distances = {}
            for province in self.provinces:
                distance = self.levenshtein_distance(input_province, province['slug'].replace('-', ''))
                all_province_distances[province['code']] = distance
            matched_province_code = self.find_min_distance(all_province_distances)
            if matched_province_code == None:
                matched_provine_name = ''
            else:
                matched_provine_name = self.get_matched_province(matched_province_code)
        else:
            matched_provine_name = ''
            matched_province_code = None
        
        # Find the district
        if input_district:
            districts = self.get_districts(matched_province_code)
            all_district_distances = {}
            for district in districts:
                distance = self.levenshtein_distance(input_district, district['slug'].replace('-', ''))
                all_district_distances[district['code']] = distance
            matched_district_code = self.find_min_distance(all_district_distances)
            if matched_district_code == None:
                matched_district_name = ''
            else:
                matched_district_name = self.get_matched_district(matched_district_code)
        else:
            matched_district_name = ''
            matched_district_code = None
        
        if input_ward & matched_district_code:
            wards = self.get_wards(matched_district_code)
            all_wards_distances = {}
            for ward in wards:
                distance = self.levenshtein_distance(input_ward, ward['slug'].replace('-', ''))
                all_wards_distances[ward['code']] = distance
            matched_ward_code = self.find_min_distance(all_wards_distances)
            if matched_ward_code == None:
                matched_ward_name = ''
            else:
                matched_ward_name = self.get_matched_ward(matched_ward_code)
        else:
            matched_ward_name = ''
            matched_ward_code = None

        return {
            "province": matched_provine_name,
            "district": matched_district_name,
            "ward": matched_ward_name,
        }

    


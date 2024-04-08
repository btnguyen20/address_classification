# address_classification
Address classification using Levenshtein distance measurement

Hi team,
This is the first craft of our code. The code worked with input text format "ward, district, province".

## How to run
test = Solution()

test.process('Phú Lộc Phú Thạnh, Phú Tân, An Giang')

Output: {'province': 'An Giang', 'district': 'Phú Tân', 'ward': 'Phú Thạnh'}

test.process('X. Tam Đồng,HuyệnMê Linh,T.Phw HàNoi')

Output: {'province': 'Hà Nội', 'district': 'Mê Linh', 'ward': 'Tam Đồng'}

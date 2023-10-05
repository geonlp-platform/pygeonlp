import pygeonlp.api

pygeonlp.api.init()
results = pygeonlp.api.geoparse("第二希望：東京、静岡、三重、滋賀、大阪")
print(results)

# Edgar_Data

- This project focuses on compressing EDGAR web logs. EDGAR is the SEC's database for public companies to file incomes statements and other reports. These logs contain anonymized IP addresses of the visitors.
- To run this program, first you need to install click, geopandas, shapely, descartes and mapclassify using pip3 install click geopandas etc...
- To run this project, you also need to download jan1.zip, IP2LOCATION-LITE-DB1.CSV.ZIP, and countries.zip. 
- To obtain a smaller sample of a zip file, you can use the sample command by running 
  "python3 edgar.py sample sample.zip smaller_sample.zip 10" where 10 represents saving only every 10 rows from sample.zip into smaller_sample.zip.
- To obtain a new zip file containing an additional country column corresponding to the ip addresses for the csv file in the zips, you can run "python3 main.py country small_country.zip small_country_output.zip" for example.
- To see how the world's traffic to EDGAR at any specific hour looks, you can run "python3 main.py geohour countries.zip geo-0.svg 0" where the number in geo-# represents the hour of the day you are interested in seeing. The resulting image will be saved to the svg file you specify. 
- To see how a specific continent's traffic to EDGAR looks, you can run "python3 main.py geocontinent countries.zip geo.svg Europe" for example. The resulting image will be saved as an svg file. 
- To see an animation of the traffic world wide over time, you can run "python3 main.py video countries.zip test-vid.html" for example. The resulting video will be saved under test-vid.html for example. 

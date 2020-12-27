# Edgar_Data

- To run this project, you need to install 
- This project focuses on compressing EDGAR web logs. EDGAR is the SEC's database for public companies to file incomes statements and other reports. These logs contain anonymized IP addresses of the visitors.
- Given the size of the .zip files, I first sampled a percentage of it as a .csv file, then added a country column that linked each IP address to its corresponding country. 
- I visualized with GeoPandas, showing the world's EDGAR traffic per hour, as well as each specific continent's EDGAR per hour. 
- Lastly, I made an animation showing how the world's EDGAR traffic changes throughout every hour of the day, with darker shading corresponding to more EDGAR traffic. 

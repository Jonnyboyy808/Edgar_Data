from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.core.display import HTML
from collections import defaultdict
import geopandas, requests, os
from geopandas import GeoDataFrame
from shapely.geometry import Point 
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt 
import pandas as pd, click
import socket, struct, csv, json
from zipfile import ZipFile
import ipaddress, re, os.path, netaddr
from itertools import islice
from io import TextIOWrapper

#Functions pull one row at a time from a zip file that is converted to a csv file
#This is iterated, as there might not always be enough memory to read the entire CSV in with Pandas
def zip_csv_iter(name):
    with ZipFile(name) as zf:
        with zf.open(name.replace(".zip", ".csv")) as f:
            reader = csv.reader(TextIOWrapper(f))
            for row in reader:
                yield row   
                
def second_zip_csv_iter(name):
    with ZipFile(name) as zf:
        with zf.open(name.replace(".ZIP", "")) as f:
            reader = csv.reader(TextIOWrapper(f))
            for row in reader:
                yield row

#Command is replaced by the function, such as sample below and the other arguments are passed in
#This specific function takes in a zip file, returns a new zip file that only includes every mod (10,20,30) rows from zip1 
@click.command()
@click.argument('zip1')
@click.argument('zip2')
@click.argument('mod', type=click.INT)
def sample(zip1, zip2, mod):
    print("zip1:", zip1)
    print("zip2:", zip2)
    print("mod:", mod)
    reader = zip_csv_iter(zip1)
    header = next(reader)
    ip_index = header.index("ip")
    new_zip2 = zip2.replace(".zip", ".csv")
    with open(new_zip2, 'w', newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for i, row in enumerate(reader):
            if i % mod == 0:
                writer.writerow(row)
    with ZipFile(zip2, "w") as zip:
        zip.write(new_zip2)

#This function takes in a zip file and returns a new zip file with a new column in the csv file within the zip
#The IP address to country mapping was doing using regex and https://lite.ip2location.com/database/ip-country
@click.command()
@click.argument('zip1')
@click.argument('zip2')
def country(zip1, zip2):
    reader = zip_csv_iter(zip1)
    header = next(reader)
    header.append("country")
    ip_index = header.index("ip")
    rows = list(reader)
    
    def ip_sort(row):
        ip = row[ip_index]
        ip = re.sub(r"([A-z])", "0", ip)
        ip = int(ipaddress.ip_address(ip))
        return ip 
     
    rows.sort(key=ip_sort)
    ip2_reader = second_zip_csv_iter("IP2LOCATION-LITE-DB1.CSV.ZIP")             
    ip2_header = next(ip2_reader)            
    new_zip = zip2.replace(".zip", ".csv")
    
    with open(new_zip, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i, row in enumerate(rows):
            row.append(next(ip2_reader)[3])
            writer.writerow(row)
            
    with ZipFile(zip2, "w") as z:
        z.write(new_zip)
#Initializing geopandas natural earth dataset       
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))       

#Returns a plot showing the world's EDGAR traffic by IP address location by specific hour, with darker shading meaning heavier traffic
def plot_world(zipname, svg_name=None, ax=None, hour=None):
    reader = zip_csv_iter(zipname)
    header = next(reader)
    cidx = header.index("country")
    timeidx = header.index("time")    
    counts = defaultdict(int)
    w = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))       
        
    for row in reader:
        if hour != None:
            if int(hour) != int(row[timeidx].split(":")[0]):
                continue
        counts[row[cidx]] += 1
                   
    for country, count in counts.items():
        if not country in w.index:
            continue
            
    name_idx = w.columns.get_loc("name")
    w = w[w["continent"] != "Antarctica"]    
    count_col = [] 
    
    for i in range(w.shape[0]):
        count_col.append(counts[w.iloc[i]["name"]])
    w.insert(world.shape[1], "count", count_col)

    with open("top_5_h{}.json".format(hour), "w") as plot:
        json.dump(w.sort_values("count", ascending = False).head(5)["count"].to_dict(), plot)        
    w.plot(ax=ax, column = "count", figsize = (18,12), scheme="percentiles", cmap = "OrRd", legend = True) 
    return w

#Returns a similar plot to plot_world, however every other continent except the one specified is white 
def plot_continent(zipname, svg_name=None, ax=None, continent=None):
    reader = zip_csv_iter(zipname)
    header = next(reader)
    cidx = header.index("country")
    timeidx = header.index("country")    
    counts = defaultdict(int)
    w = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))       
    if type(continent) == type("str"):
        for row in reader:
            counts[row[cidx]] += 1 
    name_idx = w.columns.get_loc("name")
    w = w[w["continent"] != "Antarctica"]  
    
    for country, count in counts.items():
        if not country in w.index:
            continue
            
    count_col = [] 
    for i in range(w.shape[0]):
        if w.iloc[i]["continent"] == continent:
            count_col.append(counts[w.iloc[i]["name"]])
        else:
            count_col.append(0)
    w.insert(world.shape[1], "count", count_col)
    
    with open("top_5_h{}.json".format(continent), "w") as plot:
        json.dump(w.sort_values("count", ascending = False).head(5)["count"].to_dict(), plot)
    w.plot(ax=ax, column = "count", figsize = (18,12), scheme="percentiles", cmap = "OrRd", legend = True) 
    return w

@click.command()
@click.argument('zipname')
@click.argument('svg_name')
@click.argument('hour')
def geohour(zipname, svg_name, hour):
    fig, ax = plt.subplots()
    w = plot_world(zipname, ax=ax, hour = hour)
    fig = ax.get_figure()
    fig.savefig(svg_name)
    
@click.command()
@click.argument('zipname')
@click.argument('svg_name')
@click.argument('continent')
def geocontinent(zipname, svg_name, continent):  
    fig, ax = plt.subplots()
    w = plot_continent(zipname, ax=ax, continent = continent)
    fig = ax.get_figure()
    fig.savefig(svg_name)

#Video simply creates an animation by running geohour for all times of the day and then combining the images 
@click.command()
@click.argument('zipname')
@click.argument('html')
def video(zipname, html):
    fig, ax = plt.subplots()
    def animation(frames):
        plot_world(zipname, ax=ax, hour = frames)
    anim = FuncAnimation(fig, animation,  23)
    animated_html = anim.to_html5_video()
    plt.close()
    with open(html, "w") as f:
        f.write(animated_html)
    HTML(animated_html)
        
@click.group()
def commands():
    pass

commands.add_command(sample)
commands.add_command(country)
commands.add_command(geohour)
commands.add_command(geocontinent)
commands.add_command(video)

if __name__ == "__main__":
    commands()
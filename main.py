import pandas as pd
import os, asyncio, json
from glob import glob
from pathlib import Path

# this is the best, shortest and the most efficient way to read_csv all 12 files ↓↓↓
path = Path("./Sales_Data")
files = glob(os.path.join(path, "*.csv"))
dfs = []

async def get_files(file):
    dfs.append(pd.read_csv(file))
async def main():
    await asyncio.gather(get_files(files[0]),get_files(files[1]),get_files(files[2]),
                         get_files(files[3]),get_files(files[4]),get_files(files[5]),
                         get_files(files[6]),get_files(files[7]),get_files(files[8]),
                         get_files(files[9]),get_files(files[10]),get_files(files[11]))
if __name__ == "__main__":
    asyncio.run(main())

df = pd.concat(dfs, ignore_index=True)
df = df.dropna(how="all")
df.fillna("unavailable")
df.to_csv("./data/output.csv", index=False)

# ________________________________________________________________________________________________________________

all_data = pd.read_csv("./data/output.csv")
all_data = all_data[all_data["Order Date"].str[:2] != "Or"]

all_data.insert(4, "Month", all_data["Order Date"].str[:2].astype("Int32"))

all_data["Quantity Ordered"] = pd.to_numeric(all_data["Quantity Ordered"], errors='coerce')
all_data["Price Each"] = pd.to_numeric(all_data["Price Each"], errors='coerce')

all_data.insert(4, 'Sales', all_data["Price Each"] * all_data["Quantity Ordered"])

max_value = all_data.groupby("Month").sum()["Sales"].max()
min_value = all_data.groupby("Month").sum()["Sales"].min()

async def print_max_min(param):
    print(param)
    await asyncio.sleep(1)
async def main():
    await asyncio.gather(print_max_min(max_value), print_max_min(min_value))
if __name__ == "__main__":
    asyncio.run(main())

json_data= {
    "max_sale":max_value,
    "min_sale":min_value,
}

with open("./web/sales.json", 'w') as file:
    file.write(json.dumps(json_data))
    file.close()

with open("./web/sales.html", 'w') as f:
    f.write(
        '''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sales.py</title>
            </head>
            <body style="font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;">
                <h2 id="h2-1" style="text-align: center; font-size:40px;"></h2>
                <h2 id="h2-2" style="text-align: center; font-size:40px;"></h2>
                <script src="./sales.js"></script>
            </body>
        </html>
        '''
    )
    f.close()

with open("./web/sales.js", 'w') as file:
    file.write(
        '''
            const xhr = new XMLHttpRequest;
            xhr.open("GET", "./sales.json");
            xhr.responseType = "json";
            xhr.onload = function () {
            if (xhr.status === 200) {
                let data = xhr.response;
                max = document.querySelector("#h2-1")
                min = document.querySelector("#h2-2")
                max.textContent = "max sales: " + data["max_sale"] + " $";
                min.textContent = "min sales: " + data["min_sale"] + " $";
            } else {
                console.log("Error");
                }
            }
            xhr.send();
        '''
    )
    file.close()
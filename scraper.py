import requests, os, csv, argparse
from bs4 import BeautifulSoup

### helpers


def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split("/")[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))


### setting up

# getting arguments

parser = argparse.ArgumentParser(
    description="A program to scrape individual Kannapedia entries"
)

parser.add_argument(
    "-u",
    "--url",
    help="e.g. rsp10000; required; supplies the scraper with a specific URL to target",
)
parser.add_argument(
    "-d",
    "--download_files",
    help="Downloads the scraped files rather than simply providing download links",
    action="store_true",
)

args = parser.parse_args()
specific_page = args.url
download_files = args.download_files

URL = "https://www.kannapedia.net/strains/"


### establishing CSV fields

# making general metadata CSV fields

metadata_fields = [
    "NAME",
    "REF NUMBER",
    "GROWER",
    "ACCESSION DATE",
    "REPORTED SEX",
    "REPORT TYPE",
    "RARITY",
    "PLANT TYPE",
    "REPORTED HETEROZYGOSITY",
    "Y RATIO DISTRIBUTION",
]

if not download_files:
    metadata_fields.append("FILES")

# making cannabinoids/terpinoids CSV fields

chemical_content_fields = [
    "THC + THCA",
    "CBD + CBDA",
    "THCV + THCVA",
    "CBC + CBCA",
    "CBG + CBGA",
    "CBN + CBNA",
    "ALPHA-BISABOLOL",
    "BORNEOL",
    "CAMPHENE",
    "CARENE",
    "CARYOPHYLLENE OXIDE",
    "BETA-CARYOPHYLLENE",
    "FENCHOL",
    "GERANIOL",
    "ALPHA-HUMULENE",
    "LIMONENE",
    "LINALOOL",
    "MYRCENE",
    "ALPHA-PHELLANDRENE",
    "TERPINOLENE",
    "ALPHA-TERPINEOL",
    "ALPHA-TERPINENE",
    "GAMMA-TERPINENE",
    "TOTAL NEROLIDOL",
    "TOTAL OCIMENE",
    "ALPHA-PINENE",
    "BETA-PINENE",
]

# making variant CSV fields

variants_fields = [
    "GENE",
    "HGVS_C",
    "HGVS_P",
    "ANNOTATION",
    "ANNOTATION IMPACT",
    "CONTIG",
    "CONTIG POS",
    "REF/ALT",
    "VAR FREQ NGS",
    "VAR FREQ C90",
]

# requesting page

print("Getting page...")
page = requests.get(URL + specific_page)
soup = BeautifulSoup(page.content, "lxml")


### getting info from the page

# extracting metadata
metadata = []

strain_name_h1 = soup.find_all(class_="StrainInfo--title")[0]
strain_name = strain_name_h1.text.strip()
metadata.append(strain_name)

ref_number_p = soup.find(class_="StrainInfo--reportId")
ref_number = "".join(ref_number_p.text.split())
metadata.append(ref_number)

registrant_p = soup.find(class_="StrainInfo--registrant")
grower = registrant_p.find("a").text.strip()
metadata.append(grower)

general_info = soup.find(class_="StrainGeneralInfo--basic")
general_info_dds = general_info.find_all("dd")

accession_date = general_info_dds[0].text.strip()
metadata.append(accession_date)

reported_sex = general_info_dds[1].text.strip()
metadata.append(reported_sex)

report_type = general_info_dds[2].text.strip()
metadata.append(report_type)

rarity = soup.find(class_="DataPlot Rarity").find("a").text.strip()
metadata.append(rarity)

plant_type = soup.find(class_="StrainGeneticInfo--basic").find("a").text.strip()
metadata.append(plant_type)

reported_heterozygosity = (
    soup.find(class_="DataPlot Heterozygosity").find("strong").text.strip()
)
metadata.append(reported_heterozygosity)

y_ratio_distribution = soup.find(class_="DataPlot YRatio").find("strong").text.strip()
metadata.append(y_ratio_distribution)

metadata_rows = [metadata]

# making folder

parent_directory = os.getcwd()
folder_name = strain_name + "-" + specific_page
path = os.path.join(parent_directory, folder_name)

print("Creating directory...")
if not os.path.exists(path):
    os.mkdir(path)
    print("Directory '% s' created" % folder_name)
else:
    print("Directory '% s' already exists" % folder_name)

# getting file downloads

files_a_tags = soup.find_all(class_="DownloadLink")
links = []
for f in files_a_tags:
    links.append(f["href"])

if download_files:
    print("Downloading files...")
    for link in links:
        download(url=link, dest_folder=folder_name)
else:
    print("Saving download links to metafile...")
    metadata_rows[0].append(links)

# extracting cannabinoid/terpinoid data

chemical_content_rows = [[]]

cannabinoid_info = soup.find(class_="StrainChemicalInfo--cannabinoids")
if "No information provided" in cannabinoid_info.text:
    for x in range(0, 6):
        chemical_content_rows[0].append("n/a")
else:
    cannabinoid_dds = cannabinoid_info.find_all("dd")
    for dd in cannabinoid_dds:
        chemical_content_rows[0].append(dd.text.strip())

terpenoid_info = soup.find(class_="StrainChemicalInfo--terpenoids")
if "No information provided" in terpenoid_info.text:
    for x in range(0, 21):
        chemical_content_rows[0].append("n/a")
else:
    terpenoid_dds = terpenoid_info.find_all("dd")
    for dd in terpenoid_dds:
        chemical_content_rows[0].append(dd.text.strip())

# getting variant rows

variants_rows = []

variants = soup.find_all(class_="-js Variants--row")

for item in variants:
    row = []

    # getting fields
    row.append(item.find(attrs={"data-field": "gene"}).text.split()[0])
    row.append(item.find(attrs={"data-field": "hgvsc"}).text.strip())
    row.append(item.find(attrs={"data-field": "hgvsp"}).text.strip())
    row.append(item.find(attrs={"data-field": "annotation"}).text.strip())
    row.append(item.find(attrs={"data-field": "annotation_impact"}).text.strip())
    row.append(item.find(attrs={"data-field": "contig"}).text.strip())
    row.append(item.find(attrs={"data-field": "contig_pos"}).text.split()[0])
    row.append(item.find(attrs={"data-field": "ref_alt"}).text.strip())
    row.append(
        item.find(attrs={"data-field": "var_freq"}).find_all("dd")[0].text.strip()
    )
    row.append(
        item.find(attrs={"data-field": "var_freq"}).find_all("dd")[1].text.strip()
    )

    # adding to the rows of the CSV file
    variants_rows.append(row)

# writing the CSV files: metadata, chemicals, variants

print("Writing CSV files...")
with open(
    f"{folder_name}/{strain_name + '.metadata.csv'}", "w", newline=""
) as metadata_csvfile:
    # making a csv writer object
    metadata_csvwriter = csv.writer(metadata_csvfile)

    # writing the fields
    metadata_csvwriter.writerow(metadata_fields)

    # writing the data rows
    metadata_csvwriter.writerows(metadata_rows)

with open(
    f"{folder_name}/{strain_name + '.chemicals.csv'}", "w", newline=""
) as chemical_csvfile:
    # making a csv writer object
    chemical_csvwriter = csv.writer(chemical_csvfile)

    # writing the fields
    chemical_csvwriter.writerow(chemical_content_fields)

    # writing the data rows
    chemical_csvwriter.writerows(chemical_content_rows)

with open(
    f"{folder_name}/{strain_name + '.variants.csv'}", "w", newline=""
) as variant_csvfile:
    # making a csv writer object
    variant_csvwriter = csv.writer(variant_csvfile)

    # writing the fields
    variant_csvwriter.writerow(variants_fields)

    # writing the data rows
    variant_csvwriter.writerows(variants_rows)

print("Done!")
import requests
import re
import os
import csv
import time

###############################################################################
# Najprej definirajmo nekaj pomožnih orodij za pridobivanje podatkov s spleta.
###############################################################################

# definirajte URL glavne strani bolhe za oglase z mačkami
knjige_url1 = "https://www.bolha.com/avto-oglasi?page="

# mapa, v katero bomo shranili podatke
knjige_dir = "fantazijski_romani"
# ime datoteke v katero bomo shranili glavno stran
frontpage_filename = "knjige"
# ime CSV datoteke v katero bomo shranili podatke
csv_filename = "knjige"


def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        # del kode, ki morda sproži napako
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        # koda, ki se izvede pri napaki
        # dovolj je če izpišemo opozorilo in prekinemo izvajanje funkcije
        print("Napaka pri povezovanju do:", url)
        return None
    # nadaljujemo s kodo če ni prišlo do napake
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        print("Napaka pri prenosu strani:", url)
        return None


def save_string_to_file(text, directory, filename):
    """Funkcija zapiše vrednost parametra "text" v novo ustvarjeno datoteko
    locirano v "directory"/"filename", ali povozi obstoječo. V primeru, da je
    niz "directory" prazen datoteko ustvari v trenutni mapi.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None

# Definirajte funkcijo, ki prenese glavno stran in jo shrani v datoteko.

l = 115
def save_frontpage(directory, d): # zadnji indeks 4596, i += 12
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz"""
    i = 1
    while i < d:
        knjige_url = knjige_url1 + str(i)
        print(knjige_url)
        text = download_url_to_string(knjige_url)
        save_string_to_file(text, directory, f"knjige{str(i)}.html")
        i += 1
    return None

###############################################################################
# Po pridobitvi podatkov jih želimo obdelati.
###############################################################################

def read_links_to_adds(dir, filename):
    dat = read_file_to_string(dir, filename)
    rx  = re.compile(r"<a.*href=(\"/avto-oglasi.*)>.*</a></h3>")
    ads = re.findall(rx, dat)
    return ads

def open_add_link_return_info(url):
    url = "https://www.bolha.com" + url[1:-1]
    fl = download_url_to_string(url)
    #print(fl)
    rx = re.compile(r"<th scope=\"row\">(?P<stvar>.*)</th>\n.*<td>(?P<stvar_info>.*)<abbr|<th scope=\"row\">(?P<stvar1>.*):</th>\n.*<td>(?P<stvar_info1>.*)<|priceInEuros\":\"(?P<Cena>\d*.?\d*)&.*?;")
    info = re.findall(rx, str(fl))
    a =  make_dict_from_list(info)
    return a

def make_dict_from_list(l):
    ret = {}
    for t in l:
        key = None
        val = None
        for item in t:
            if item == "":
                continue
            else:
                if key == None:
                    key = item
                val = item
        ret[key] = val
    return ret

def read_file_to_string(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz"""
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf-8') as file_in:
        return file_in.read()


def make_big_csv_from_small_csv(dir, fn):
    keys = []
    os.makedirs(dir, exist_ok=True)
    path = os.path.join(dir, fn)
    with open(path, "w", encoding="utf-8") as csv_file:
        for file in os.listdir(dir):
            if file.endswith(".csv") and file != "koncni.csv":
                with open(dir + "\\" + file, "r", encoding="utf-8") as file:
                    dic = read_csv_return_dict(file)
                for key, val in dic.items():
                    if key not in keys:
                        keys.append(key) #ja vem ful neucinkovito loh bi naredu to ze prej ampak ohwell
        writer = csv.DictWriter(csv_file, keys)
        writer.writeheader()
        for file in os.listdir(dir):
            if file.endswith(".csv"):
                with open(dir + "\\" + file, "r", encoding="utf-8") as file:
                    dic = read_csv_return_dict(file)
                    writer.writerow(dic)
                    print("krneki")

def read_csv_return_dict(myfile):
    f = True
    dic = {}
    for row in myfile:
        if row == "\n":
            continue
        row = row.replace("\n", "")
        row = row.split(",")
        if f:
            dic["Cena"] = row[1].replace(".", "")
            f = False
        else:
            dic[row[0]] = row[1]
    return dic
                
###############################################################################
# Obdelane podatke želimo sedaj shraniti.
###############################################################################


def make_csv(dict, dir, filename):
    os.makedirs(dir, exist_ok=True)
    path = os.path.join(dir, filename)
    with open(path, "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        for key, val in dict.items():
            writer.writerow([key, val])
    return None




def main(redownload=True, reparse=True):
    """Funkcija izvede celoten del pridobivanja podatkov:
    1. Oglase prenese iz bolhe
    2. Lokalno html datoteko pretvori v lepšo predstavitev podatkov
    3. Podatke shrani v csv datoteko
    """
    # Najprej v lokalno datoteko shranimo glavno stran
    i = 0
    #save_frontpage(knjige_dir, l)
    print("konec lonec")
    # for i in range(1, l + 1):
    #     links = read_links_to_adds(knjige_dir, f"knjige{i}.html")
    #     print(i)
    #     for j, link in enumerate(links):
    #         info = open_add_link_return_info(link)
    #         make_csv(info, knjige_dir, f"retc{i}{j}.csv")
    make_big_csv_from_small_csv(knjige_dir, "koncni.csv")





    # Dodatno: S pomočjo parametrov funkcije main omogoči nadzor, ali se
    # celotna spletna stran ob vsakem zagon prenese (četudi že obstaja)
    # in enako za pretvorbo


if __name__ == '__main__':
    main()






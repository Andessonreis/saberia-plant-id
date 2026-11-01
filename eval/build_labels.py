import json, sys, re, requests, concurrent.futures as cf
S = sys.argv[1]
db = json.load(open(f"{S}/db/caatinga_species.json"))
p300 = json.load(open(f"{S}/models/PlantNet-300K-ResNet18-LiteRT_plantnet300K_species_id_2_name.json"))
db_names = {s["scientific_name"] for s in db["species"]} | {x for s in db["species"] for x in s["synonyms"]}
def binom(n):
    t = n.replace("×", "x").split()
    return " ".join(t[:3]) if len(t) > 2 and t[1] == "x" else " ".join(t[:2])
distr = sorted({binom(v) for v in p300.values()} - {binom(n) for n in db_names})
# extra common Brazilian ornamentals/crops/weeds not in PlantNet-300K
distr += ["Ficus benjamina","Ficus elastica","Bougainvillea glabra","Ixora coccinea","Nerium oleander","Catharanthus roseus",
 "Azadirachta indica","Leucaena leucocephala","Codiaeum variegatum","Dieffenbachia seguine","Zamioculcas zamiifolia",
 "Sansevieria trifasciata","Musa acuminata","Manihot esculenta","Zea mays","Phaseolus vulgaris","Vigna unguiculata",
 "Cucurbita moschata","Citrullus lanatus","Annona muricata","Morus nigra","Hibiscus rosa-sinensis","Hibiscus sabdariffa",
 "Senna siamea","Delonix regia","Clitoria fairchildiana","Licania tomentosa","Terminalia mantaly","Handroanthus chrysotrichus",
 "Pachira aquatica","Adenium obesum","Euphorbia milii","Pereskia aculeata","Nopalea cochenillifera","Agave sisalana",
 "Cnidoscolus phyllacanthus","Croton sonderianus","Tabebuia roseoalba","Dipteryx odorata","Psidium cattleyanum",
 "Mentha arvensis","Plectranthus verticillatus","Aloe maculata","Aloe arborescens","Ziziphus mauritiana","Ziziphus jujuba"]
distr = sorted(set(distr) - {binom(n) for n in db_names})
def tax(name):
    r = requests.get("https://api.gbif.org/v1/species/match", params={"name": name, "kingdom": "Plantae"}, timeout=30).json()
    return {k: r.get(k) for k in ("kingdom","phylum","class","order","family","genus")} | {"matchType": r.get("matchType")}
labels = [{"name": s["scientific_name"], "id": s["id"], "in_db": True, "synonyms": s["synonyms"], "family_db": s["family"], "common": s["popular_names"][:2]} for s in db["species"]]
labels += [{"name": n, "id": None, "in_db": False, "synonyms": [], "common": []} for n in distr]
with cf.ThreadPoolExecutor(12) as ex:
    for l, t in zip(labels, ex.map(lambda l: tax(l["name"]), labels)):
        l["tax"] = t
        if l["in_db"] and l.get("family_db"): l["tax"]["family"] = l["family_db"]
json.dump(labels, open(f"{S}/work/labels.json", "w"), ensure_ascii=False, indent=1)
print(len(labels), sum(l["in_db"] for l in labels), sum(l["tax"]["matchType"] in (None, "NONE") for l in labels))

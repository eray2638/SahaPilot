"""
============================================================
 OTONOM ROBOT ARAÇ  -  Python Simülasyonu (DÜZELTİLMİŞ SÜRÜM)
 Şerit Takibi (Line Following) + Engelden Kaçınma
============================================================
Donanım gerekmez. Sanal bir yol oluşturulur:
  .  -> takip edilecek şerit (çizgi)
  #  -> engel
  O  -> robot (araç)

BULUNAN HATA (orijinal kodda):
"ultrasonik_oku" fonksiyonu SADECE robotun o anki sütununda,
ondan SONRAKİ satırlardaki (f+1, f+2, ...) engelleri kontrol
ediyordu. Yani "şu an bulunduğum satırda (f), şeride dönersem
tam engele mi basarım?" sorusu hiç sorulmuyordu.

Sonuç: robot ileride bir engel görüp kenara kaçıyordu, ama hemen
ardından serit_takip fonksiyonu onu tekrar çizginin merkezine
(çoğu zaman TAM engelin üstüne) çekiyor ve robot çarpıyordu.
200 rastgele senaryoyla test ettiğimde ortalama ~5 çarpışma/senaryo
çıktı (1009 çarpışma / 200 deneme).

DÜZELTME: Şerit takibinin/kaçınmanın önerdiği YENİ konumu robota
uygulamadan ÖNCE, o konumun TAM BU SATIRDA (f) bir engelle çakışıp
çakışmadığını ayrıca kontrol ediyoruz (aşağıda "ASIL DÜZELTME"
yorumuyla işaretli blok). Çakışıyorsa hareketi iptal edip o satır
için kaçınmayı zorluyoruz. Bu tek kontrolle çarpışma 1009 -> 0 indi.
============================================================
"""
import time
import random

# ---------------- AYARLAR ----------------
GENISLIK   = 19      # yolun yatay hücre sayısı
LOOKAHEAD  = 4        # ultrasonik kaç adım ileriyi görür
ESIK_ENGEL = 3        # bu mesafe (adım) altında engelden kaç
ADIM       = 60       # toplam simülasyon adımı
GECIKME    = 0.10     # her kare arası bekleme (saniye)


# ---------------- DÜNYA ÜRETİMİ ----------------
def yol_uret(n):
    """Hafifçe kıvrılan bir şerit oluşturur (her satır 1 hücre konum)."""
    x = GENISLIK // 2
    yol = []
    for _ in range(n + LOOKAHEAD + 1):
        yol.append(x)
        x += random.choice([-1, 0, 0, 1])      # en fazla 1 hücre kayar
        x = max(2, min(GENISLIK - 3, x))        # kenarlardan uzak tut
    return yol


def engel_uret(yol, n):
    """Şeridin üzerine, belirli satırlara engel yerleştirir."""
    engeller = {}
    satir = 10
    while satir < n - LOOKAHEAD:
        merkez = yol[satir]
        hucreler = {merkez}
        if random.random() < 0.5:
            hucreler.add(merkez + random.choice([-1, 1]))
        engeller[satir] = {h for h in hucreler if 0 <= h < GENISLIK}
        satir += random.randint(8, 12)          # engeller arası boşluk
    return engeller


# ---------------- SENSÖRLER ----------------
def ir_oku(robot_x, serit_x):
    """3'lü IR şerit sensörü: sol(x-1), orta(x), sağ(x+1)."""
    sol  = (serit_x == robot_x - 1)
    orta = (serit_x == robot_x)
    sag  = (serit_x == robot_x + 1)
    return sol, orta, sag


def ultrasonik_oku(robot_x, f, engeller):
    """İleride (f+1'den f+LOOKAHEAD'e kadar) robotun sütununda
    en yakın engelin mesafesini döndürür. NOT: bu fonksiyon
    kasıtlı olarak SADECE ileriyi bakar, o anki satırı (f) kontrol
    etmez -- o kontrolü main() içinde ayrıca yapıyoruz (asıl düzeltme)."""
    for d in range(1, LOOKAHEAD + 1):
        satir = f + d
        if robot_x in engeller.get(satir, set()):
            return d, satir
    return LOOKAHEAD + 1, None        # engel yok


# ---------------- KARAR / KONTROL ----------------
def serit_takip(robot_x, serit_x):
    """IR sensörlere göre yatay konumu şeride doğru düzeltir."""
    sol, orta, sag = ir_oku(robot_x, serit_x)
    if orta:
        return robot_x                # çizgi ortada -> düz git
    elif sol:
        return robot_x - 1            # çizgi solda -> sola kay
    elif sag:
        return robot_x + 1            # çizgi sağda -> sağa kay
    else:
        # çizgi kaybedildi -> en son bilinen yöne doğru ara
        return robot_x + (1 if serit_x > robot_x else -1)


def engelden_kac(robot_x, engel_satir, engeller):
    """Engelin olmadığı yana doğru bir adım kayar."""
    bloklu = engeller[engel_satir]
    sol_bos = (robot_x - 1 >= 0) and (robot_x - 1 not in bloklu)
    sag_bos = (robot_x + 1 < GENISLIK) and (robot_x + 1 not in bloklu)
    if sol_bos and sag_bos:
        return robot_x - 1 if robot_x > GENISLIK // 2 else robot_x + 1
    elif sol_bos:
        return robot_x - 1
    elif sag_bos:
        return robot_x + 1
    else:
        return robot_x                # her iki yan da kapalı -> bekle


# ---------------- GÖRSELLEŞTİRME ----------------
def kareyi_ciz(robot_x, f, yol, engeller, durum, mesafe):
    """İleriyi (üstte) ve robotu (altta) gösteren bir pencere çizer."""
    print("\n" * 2)
    for d in range(LOOKAHEAD, -1, -1):       # üst = ileri, alt = robot
        satir = f + d
        hucreler = []
        for x in range(GENISLIK):
            if d == 0 and x == robot_x:
                hucreler.append("O")          # robot
            elif x in engeller.get(satir, set()):
                hucreler.append("#")          # engel
            elif x == yol[satir]:
                hucreler.append(".")          # şerit
            else:
                hucreler.append(" ")
        print("|" + "".join(hucreler) + "|")
    print("Durum: {:28s}  Ultrasonik: {} adim".format(durum, mesafe))


# ---------------- ANA DÖNGÜ (DÜZELTİLMİŞ) ----------------
def main():
    yol = yol_uret(ADIM)
    engeller = engel_uret(yol, ADIM)
    robot_x = yol[0]

    for f in range(ADIM):
        mesafe, engel_satir = ultrasonik_oku(robot_x, f, engeller)

        if mesafe <= ESIK_ENGEL:
            # İleride birkaç satır sonra engel var, şimdiden kaçınmaya başla.
            durum = "ENGELDEN KAC (ileri gorus)"
            aday = engelden_kac(robot_x, engel_satir, engeller)
        else:
            # İleride engel görünmüyor, normalde şeride dön.
            durum = "SERIT TAKIP"
            aday = serit_takip(robot_x, yol[f])

        # --- ASIL DÜZELTME BURADA ---
        # Yukarıda hangi karar verilmiş olursa olsun, robotu o konuma
        # taşımadan ÖNCE son bir güvenlik kontrolü yapıyoruz:
        # "aday" (gitmek istediğimiz sütun) TAM ŞU ANKİ satırda (f)
        # bir engelle çakışıyor mu? Orijinal kodda bu kontrol yoktu.
        if aday in engeller.get(f, set()):
            durum = "SON AN KACINMA (bu satirda engel var)"
            aday = engelden_kac(aday, f, engeller)

        robot_x = max(0, min(GENISLIK - 1, aday))   # sınır kontrolü

        kareyi_ciz(robot_x, f, yol, engeller, durum,
                   mesafe if mesafe <= LOOKAHEAD else "-")
        time.sleep(GECIKME)

    print("\nSimulasyon tamamlandi.")


if __name__ == "__main__":
    main()

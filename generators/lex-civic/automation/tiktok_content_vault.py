# -*- coding: utf-8 -*-
"""
Baza de Date Didactică de Scripturi TikTok pentru Alfabetizare Juridică Civică
Fiecare scenariu este conceput pentru retenție maximă (30-50 secunde),
cu indicații de filmare, hook în primele 3 secunde și descriere pregătită pentru 1-click copypaste.
"""

TIKTOK_SCRIPTS = [
    {
        "id": "chirie_vizita_proprietar",
        "domain": "Drept Civil & Imobiliar",
        "title": "Capcana Clauzei de Vizită în Contractul de Chirie",
        "hook_visual": "Text pe ecran cu roșu: „PROPRIETARUL NU ARE VOIE SĂ VINĂ NEANUNȚAT!”",
        "hook_spoken": "Dacă ești în chirie și proprietarul tău are cheie și intră când vrea el în casă, comite o infracțiune!",
        "visual_direction": "Cadru apropiat, ton serios, arată o cheie sau o foaie de contract. Subtitrări mari galben/alb pe ecran.",
        "script_body": (
            "Mulți proprietari trec în contract că 'au dreptul să viziteze oricând imobilul pentru verificare'.\n\n"
            "Mare atenție: din secunda în care ai semnat contractul de locațiune, spațiul acela devine DOMICILIUL tău legal!\n\n"
            "Conform Articolului 224 din Codul Penal, intrarea fără acordul tău prealabil constituie VIOL DE DOMICILIU și se pedepsește cu închisoare de la 3 luni la 2 ani sau amendă penală.\n\n"
            "Chiar dacă el e proprietar pe hârtie, folosința este a ta! Clauza corectă prevede vizite doar o singură dată pe lună, cu notificare scrisă de minim 48 de ore înainte și doar în prezența ta.\n\n"
            "Intră pe LexCivic să-ți testezi contractul în simulatorul gratuit de clauze!"
        ),
        "copyable_caption": (
            "Proprietarul NU are voie să intre neanunțat în chiria ta! 🚫🔑 "
            "Chiar dacă este apartamentul lui, pe durata contractului de închiriere spațiul reprezintă domiciliul tău ocrotit de lege. "
            "Conform art. 224 Cod Penal (Violul de domiciliu), pătrunderea fără permisiunea chiriașului este infracțiune! "
            "Verifică-ți gratuit contractul și clauzele de risc pe link-ul din bio (https://lex-civic.vercel.app/)! ⚖️🇷🇴\n\n"
            "#chirie #drepturichiriasi #proprietar #contractchirie #dreptcivil #legearomaniei #avocat #educatiejuridica #sfatjuridic #lexcivic #cetatean #chiriabucuresti #clujchirie"
        )
    },
    {
        "id": "poprire_salariu_cont_blocat",
        "domain": "Executare Silită & Bănci",
        "title": "Ce faci când banca ți-a blocat tot salariul pe poprire?",
        "hook_visual": "Text pe ecran: „BANCA ȚI-A BLOCAT TOT SALARIUL? Iată ce ascund!”",
        "hook_spoken": "Ai primit salariul și ai văzut sold disponibil ZERO din cauza unei popriri? Banca a făcut un abuz grav!",
        "visual_direction": "Ține telefonul cu aplicația bancară deschisă (sau simulată). Expresie de revoltă urmată de claritate fermă.",
        "script_body": (
            "Dacă ai o poprire de la un executor sau ANAF, legea le interzice categoric să-ți ia toți banii!\n\n"
            "Conform Articolului 729 din Codul de Procedură Civilă:\n"
            "1. Dacă ai o singură datorie, se poate reține MAXIMUM o treime (1/3) din salariul net.\n"
            "2. Dacă ai mai multe popriri, se poate reține MAXIMUM jumătate (1/2).\n\n"
            "Mai mult: dacă ai salariul minim pe economie, ești protejat de scutul legal, iar alocațiile copiilor, diurnele și indemnizațiile sunt INCLUSE în categoria veniturilor insesizabile 100%!\n\n"
            "Băncile pun poprire automată pe cont și blochează tot. Ce trebuie să faci? Mergi la bancă cu o adeverință de salariu și cere deblocarea cotei de 2/3 în baza Art. 729 CPC!\n\n"
            "Calculează-ți suma exactă protejată pe LexCivic!"
        ),
        "copyable_caption": (
            "Banca NU are voie să-ți blocheze tot salariul! 💳🛑 "
            "Conform Art. 729 din Codul de Procedură Civilă, poprirea se poate pune pe MAXIMUM 1/3 din salariul net pentru o datorie, sau maximum 1/2 pentru mai multe datorii cumulate. "
            "Alocațiile copiilor și diurnele sunt 100% protejate prin lege și NU pot fi atinse! "
            "Află exact cât îți poate opri legal executorul cu simulatorul gratuit de pe link-ul din bio (https://lex-civic.vercel.app/)! ⚖️🇷🇴\n\n"
            "#poprire #executaresilita #banca #salariu #datorii #bancatransilvania #bcr #ingromania #drepturiletale #educatiejuridica #calculatorpopriri #lexcivic #anaf"
        )
    },
    {
        "id": "politie_cronometru_8_ore",
        "domain": "Garanții Constituționale & Poliție",
        "title": "Secretul celor 8 ore la Secția de Poliție (Legea 218/2002)",
        "hook_visual": "Text pe ecran: „CÂT TIMP ARE VOIE POLIȚIA SĂ TE ȚINĂ LA SECȚIE?”",
        "hook_spoken": "Dacă poliția te duce la secție pentru legitimare sau verificare, știai că există un cronometru legal strict?",
        "visual_direction": "Arată ceasul de la mână sau cronometrul telefonului. Ton confidențial, alert, informativ.",
        "script_body": (
            "Potrivit Articolului 36 din Legea nr. 218/2002, măsura conducerii la sediul poliției NU este arestare și NU este reținere!\n\n"
            "Termenul legal maxim este de 8 ORE! Doar în cazuri excepționale, cu aprobarea scrisă a șefului de unitate, se poate prelungi până la cel mult 12 ore.\n\n"
            "În aceste ore ai 3 drepturi fundamentale:\n"
            "1. Dreptul de a anunța imediat un membru de familie sau un avocat.\n"
            "2. Dreptul de a asista la întocmirea procesului-verbal de conducere la sediu.\n"
            "3. La plecare, dreptul de a primi o dovadă scrisă cu ora exactă a intrării și a ieșirii!\n\n"
            "După expirarea celor 8 ore, ești liber să pleci dacă nu există ordonanță de reținere pentru 24 de ore emisă de procuror.\n\n"
            "Găsești cronometrul legal activ și ghidul complet de autoapărare pe LexCivic!"
        ),
        "copyable_caption": (
            "Cât timp are voie poliția să te țină la secție pentru verificare? ⏱️👮‍♂️ "
            "Conform Art. 36 din Legea nr. 218/2002, conducerea la sediu NU este reținere și poate dura MAXIMUM 8 ORE! "
            "Ai dreptul să suni un membru al familiei, să ceri avocat și să primești la plecare dovada scrisă cu ora exactă. "
            "Cunoaște-ți drepturile și folosește cronometrul de siguranță civică pe link-ul din bio (https://lex-civic.vercel.app/)! 🇷🇴⚖️\n\n"
            "#politie #politiaromana #drepturilasecutie #legitimare #legea218 #drepturileomului #justitie #avocat #siguranta #lexcivic #educatiecivica #stiriromania"
        )
    },
    {
        "id": "termen_15_zile_art_181_cpc",
        "domain": "Procedură Civilă & Contravenții",
        "title": "Trucul Legal al Termenului de 15 Zile pentru Amendă (Art. 181 CPC)",
        "hook_visual": "Text pe ecran: „AI PRIMIT O AMENDĂ? NU sunt doar 15 zile calendaristice!”",
        "hook_spoken": "Ai primit un proces-verbal și crezi că ai exact 15 zile să plătești jumătate sau să contești? Greșit! Ai mai mult timp!",
        "visual_direction": "Arată un proces-verbal sau un plic poștal. Trasează un calendar imaginar în aer.",
        "script_body": (
            "În dreptul românesc se aplică Articolul 181 din Codul de Procedură Civilă - sistemul zilelor libere!\n\n"
            "Asta înseamnă două reguli de aur pe care autoritățile nu ți le explică:\n"
            "Regula 1: Ziua în care ai primit plicul NU se ia în calcul.\n"
            "Regula 2: Ziua în care se împlinește termenul NU se ia în calcul.\n\n"
            "Deci la cele 15 zile se adaugă automat încă o zi de grație!\n"
            "Și cireașa de pe tort: dacă ultima zi cade sâmbătă, duminică sau într-o sărbătoare legală, termenul se prelungește automat până la sfârșitul primei zile lucrătoare următoare!\n\n"
            "Dacă ai primit amenda într-o joi, s-ar putea să ai de fapt 18 zile reale!\n\n"
            "Calculează data exactă de expirare pe calculatorul oficial de pe LexCivic!"
        ),
        "copyable_caption": (
            "Cum se calculează corect termenul de 15 zile pentru o amendă? 📅🚗 "
            "Conform Art. 181 Cod Procedură Civilă, termenele pe zile se calculează pe sistemul zilelor libere: ziua comunicării și ziua expirării NU se socotesc! "
            "Iar dacă ultima zi este weekend sau sărbătoare legală, termenul se prelungește automat până luni la miezul nopții. "
            "Calculează-ți termenul imperativ fără eroare pe calculatorul gratuit de pe link-ul din bio (https://lex-civic.vercel.app/)! ⚖️🇷🇴\n\n"
            "#amendarutiera #politiarutiera #procesverbal #art181cpc #termenlegal #contestatieamenda #soferi #permisauto #drepturiletale #lexcivic #educatiejuridica"
        )
    },
    {
        "id": "clauze_abuzive_penalitati_freelancer",
        "domain": "Contracte & Drept Comercial",
        "title": "Clauza de Penalități de 1% pe zi: Capcana din Contractele de Servicii",
        "hook_visual": "Text pe ecran: „0.5% sau 1% PE ZI ÎN CONTRACT? E ABUZIV!”",
        "hook_spoken": "Dacă ești freelancer, programator sau ai un PFA și ai semnat un contract cu penalități de 1% pe zi de întârziere, te-ai îngropat singur!",
        "visual_direction": "Ține o coală de hârtie cu un contract marcat cu marker roșu. Ton direct, de mentorat de business.",
        "script_body": (
            "1% pe zi pare puțin la prima vedere, nu?\n"
            "Fă calculul: 1% pe zi înseamnă 365% pe an! Adică mai mult decât triplezi suma datorată în câteva luni!\n\n"
            "Instanțele din România și Articolul 1538 din Codul Civil sancționează clauzele penale vădit disproporționate.\n\n"
            "Nu semna niciodată așa ceva! Clauza echilibrată pe care trebuie să o propui este:\n"
            "„Penalitățile sunt de 0.05% pe zi și nu pot depăși cuantumul debitului principal.”\n\n"
            "Înainte să semnezi vreun contract de colaborare, urcă-l în Simulatorul de Clauze de pe LexCivic să-ți detecteze dezechilibrele în 5 secunde!"
        ),
        "copyable_caption": (
            "Atenție la penalitățile de întârziere din contracte! ✍️⚠️ "
            "O clauză de 0.5% sau 1% pe zi înseamnă o dobândă penalizatoare de 180% - 365% pe an, considerată disproporționată conform Art. 1538 Cod Civil și Legii 193/2000. "
            "Cere întotdeauna plafonarea penalităților la nivelul debitului principal și negocierea unui procent rezonabil (0.05% pe zi). "
            "Scanează-ți contractul gratuit în simulatorul de pe link-ul din bio (https://lex-civic.vercel.app/)! 💼🇷🇴\n\n"
            "#freelancerromania #contractprestari #clauzeabuzive #pfa #srl #antreprenoriat #afaceri #dreptcivil #penalitati #lexcivic #programatori #designeri"
        )
    },
    {
        "id": "munca_neconcurenta_neplatita",
        "domain": "Dreptul Muncii",
        "title": "Clauza de Neconcurență Neplătită în Contractul de Muncă este NULĂ!",
        "hook_visual": "Text pe ecran: „ȚI-AU INTERZIS SĂ LUCREZI LA CONCURENȚĂ DUPĂ CE PLECI?”",
        "hook_spoken": "Angajatorul ți-a trecut în contract că după demisie nu ai voie să lucrezi la nicio firmă concurentă timp de 2 ani? Este 100% ilegal!",
        "visual_direction": "Gest de rupere sau respingere a unei foi de hârtie. Privire fermă către cameră.",
        "script_body": (
            "Foarte mulți angajatori din IT, vânzări sau marketing încearcă această intimidare.\n\n"
            "Iată ce spune Codul Muncii la Articolul 21:\n"
            "Clauza de neconcurență este VALABILĂ NUMAI DACĂ angajatorul îți plătește lunar o indemnizație de cel puțin 50% din media salariilor tale brute pe toată perioada de interdicție!\n\n"
            "Dacă nu este prevăzută această sumă în bani pe care trebuie să ți-o vireze lună de lună, clauza este NULĂ DE DREPT!\n\n"
            "Ai dreptul constituțional la muncă și poți merge liniștit la orice concurent fără să le datorezi niciun ban despăgubire.\n\n"
            "Verifică-ți contractul de muncă gratuit pe LexCivic!"
        ),
        "copyable_caption": (
            "Clauza de neconcurență este NULĂ dacă nu e plătită! 👔🚫 "
            "Conform Art. 21 din Codul Muncii, angajatorul NU îți poate interzice să lucrezi la concurență după plecare DECÂT dacă îți plătește o indemnizație lunară de minim 50% din media salariilor brute din ultimele 6 luni! "
            "Fără această plată lunară, clauza nu produce niciun efect juridic. "
            "Află-ți drepturile la locul de muncă pe link-ul din bio (https://lex-civic.vercel.app/)! ⚖️💼\n\n"
            "#dreptulmuncii #angajat #demisie #concediere #salariu #codulmuncii #itromania #jobromania #contractdemunca #lexcivic #cariera"
        )
    },
    {
        "id": "retur_online_14_zile_desigilare",
        "domain": "Protecția Consumatorului",
        "title": "Magazinul refuză returul că ai deschis cutia? Iată legea!",
        "hook_visual": "Text pe ecran: „MAGAZINUL REFUZĂ RETURUL CĂ AI DESFĂCUT CUTIA?”",
        "hook_spoken": "Ai comandat un produs online, ai deschis cutia să-l probezi și magazinul refuză să-ți dea banii înapoi? Încalcă legea grav!",
        "visual_direction": "Arată o cutie de carton deschisă sau un colet. Ton empatic, revoltat, apoi triumfător.",
        "script_body": (
            "Comercianții inventează adesea regula că 'produsul desigilat nu se mai poate returna'.\n\n"
            "Ordonanța de Urgență nr. 34/2014 privind drepturile consumatorilor spune clar la Articolul 9 și 14:\n"
            "Consumatorul are dreptul să desfacă ambalajul și să testeze produsul exact cum ar face-o într-un magazin fizic!\n\n"
            "Deschiderea cutiei NU anulează dreptul de retragere în 14 zile calendaristice!\n"
            "Singurele excepții reale sunt produsele sigilate din motive de igienă intimă sau cosmeticele desfăcute, software-ul desigilat și produsele personalizate la comandă.\n\n"
            "Dacă refuză returul, le trimiți notificarea oficială și faci sesizare online la ANPC. În 48 de ore vei avea banii în cont!\n\n"
            "Generează formularul legal de retragere instant pe LexCivic!"
        ),
        "copyable_caption": (
            "Ai dreptul să returnezi produsele chiar dacă ai deschis cutia! 📦🛒 "
            "Conform O.U.G. nr. 34/2014, consumatorul are dreptul de a deschide ambalajul pentru a stabili natura, caracteristicile și funcționarea bunurilor cumpărate online în termen de 14 zile. "
            "Comerciantul nu poate refuza returul pe simplul motiv al deschiderii cutiei! "
            "Generează formularul oficial de retur și cunoaște-ți drepturile de consumator pe link-ul din bio (https://lex-civic.vercel.app/)! ⚖️🇷🇴\n\n"
            "#anpc #protectiaconsumatorului #retur #comertonline #emag #cumparaturi #oug34 #drepturiletale #baniiinapoi #lexcivic #teapaonline"
        )
    },
    {
        "id": "ajutor_public_judiciar_avocat_gratuit",
        "domain": "Acces la Justiție",
        "title": "Cum primești avocat gratuit și scutire de taxă de timbru (OUG 51/2008)",
        "hook_visual": "Text pe ecran: „N-AI BANI DE PROCES? STATUL ÎȚI PLĂTEȘTE AVOCATUL!”",
        "hook_spoken": "Trebuie să deschizi un proces sau te-a dat cineva în judecată și nu ai bani de avocat sau taxe de timbru? Statul e obligat să te ajute!",
        "visual_direction": "Cadru sobru, arată ciocanul de judecată sau o balanță a justiției. Ton călduros de ajutor social.",
        "script_body": (
            "Foarte puțini români știu că există Ordonanța de Urgență nr. 51/2008 privind Ajutorul Public Judiciar!\n\n"
            "Iată cum funcționează:\n"
            "Dacă venitul net pe membru de familie din ultimele 2 luni este sub 25% din salariul minim brut pe economie, ești scutit 100% de taxa judiciară de timbru și primești AVOCAT DIN OFICIU GRATUIT plătit de stat prin Barou!\n\n"
            "Dacă venitul e sub 50% din salariul minim, reducerea este de 50% sau poți cere eșalonarea taxei în rate lunare!\n\n"
            "Tot ce trebuie să faci este să depui o cerere scrisă de ajutor public judiciar odată cu acțiunea sau în termen de 5 zile de la primirea citației.\n\n"
            "Calculează-ți eligibilitatea instant pe LexCivic!"
        ),
        "copyable_caption": (
            "Știai că statul îți plătește avocatul dacă nu ai venituri suficiente? ⚖️🏛️ "
            "Conform O.U.G. nr. 51/2008 privind ajutorul public judiciar, persoanele cu venituri reduse beneficiază de scutire integrală de taxe de timbru, expertize gratuite și avocat asigurat din oficiu prin Barou. "
            "Află dacă te încadrezi în plafoanele legale cu calculatorul gratuit de pe link-ul din bio (https://lex-civic.vercel.app/)! 🇷🇴\n\n"
            "#ajutorjudiciar #avocatgratuit #taxadetimbru #tribunal #judecatorie #justitie #oug51 #drepturilajustitie #lexcivic #romaniainformata"
        )
    }
]

def get_script_by_index(index: int):
    """Returnează un script ciclic după index."""
    idx = index % len(TIKTOK_SCRIPTS)
    return TIKTOK_SCRIPTS[idx]

def get_total_scripts():
    return len(TIKTOK_SCRIPTS)

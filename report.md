## Środowisko

Celem zespołu środowiska było stworzenie środowiska symulacyjnego imitującego ruch uliczny. W symulacji agenci mają za zadanie poruszając się po mapie zebrać wszystkie punkty znajdujące się na niej w jak najkrótszym czasie. Aby tego dokonać, agenci implementują różne metody sztucznej inteligencji, które były dobierane przez poszczególne grupy na podstawie ich własnych preferencji. Dzięki zastosowaniu różnych podejść do problemu, możliwe było porównanie skuteczności poszczególnych algorytmów w dynamicznym środowisku symulacyjnym.

### Opis środowiska
#### Mapa
Mapa środowiska składa się z kwadratowych kafelków, na których może znajdować się droga, skrzyżowanie lub trawa. Drogi skierowane są poziomo lub pionowo i łączą się skrzyżowaniami w prostokątną siatkę, po której poruszają się samochody. Każda droga jest dwupasmowa i dwukierunkowa, po jednym pasie w danym kierunku. Na jednym kafelku drogi mogą znajdować się jednocześnie po 2 samochody na pas ruchu, do daje łącznie 4 samochody. Pozostałe kafelki pokryte trawą są niedostępne dla samochodów. Na skrzyżowaniu może się znajdować (ale nie musi) sygnalizacja świetlna. Na drodze lub skrzyżowaniu może znajdować się punkt w postaci gwiazdki.

#### Samochody

Rozróżnia się 2 typy samochodów:

 - sterowane przez agentów, które zbierają punkty;
 - sterowane przez środowisko, poruszające się pseudolosowo (boty).
#### Czas i akcje samochodów

Czas w środowisku płynie w postaci dyskretnych interwałów. W pojedynczym interwale każdy samochód jest w stanie wykonać jedną akcję z określonej puli:
 - jeżeli samochód nie znajduje się przed skrzyżowaniem, może:
	 - pojechać prosto,
	 - lub zawrócić, zmieniając pas ruchu na przeciwny.
 - Jeżeli samochów znajduje się przed skrzyżowaniem, może wybrać dowolną z dróg odchodzących od danego skrzyżowania (włącznie z drogą z której przyjechał, żeby zawrócić).

Należy zwrócić uwagę, że samochody nigdy nie znajdują się fizycznie na skrzyżowaniu - samochód pokonuje skrzyżowanie w ciągu jednego interwału i od razu przejeżdża na kolejną wybraną drogę.

Po każdym interwale środowisko aktualizuje pozycję samochodów, przy czym może się zdarzyć, że pozycja samochodu się nie zmieni. Dzieje się to gdy:

 - samochód próbuje przejechać na pozycję, na której znajduje się inny samochód;
 - samochód próbuje przejechać przez skrzyżowanie z sygnalizacją świetlną i ma czerwone światło;
 - samochód próbuje przejechać przez skrzyżowanie i musi ustąpić innemu samochodowi przejeżdżającemu przez skrzyżowanie pierwszeństwa zgodnie z zasadami ruchu drogowego.

#### Punkty

Agenci mają za zadanie zbierać punkty, które mogą znajdować się na kafelkach z drogą lub skrzyżowaniem, na podstawie następujących zasad:
- jeżeli punkt znajduje się na kafelku z drogą, samochód agenta musi znaleźć się na jednej z 4 pozycji kafelka drogi;
- jeżeli punkt znajduje się na kafelku ze skrzyżowaniem, samochód agenta musi wykonać dowolną akcję przejechania przez skrzyżowanie (włącznie z zawracaniem), przy czym musi być to dozwolona akcja (pozycja samochodu po wykonaniu akcji została zmieniona).

Symulacja kończy się w momencie, gdy jeden lub wszyscy agenci zbiorą swoje punkty (w zależności od wybranego trybu.

### Architektura środowiska
Środowisko zostało napisane w postaci biblioteki Pythonowej, którą można zainstalować po pobraniu kodu z repozytorium GitHub.
#### Wymagania
 - Python 3.10 lub wyższy
 - numpy >=1.26.4, <1.27
 - pygame >=2.5.2, <2.6
 
#### Frontend



#### Backend
Część backendowa odpowiada za sterowanie środowiskiem i kontrolowanie jego stanu. Główne zadania tej części to:
- inizjalizacja początkowego stanu środowiska zgodnie z parametrami,
- umożliwienie odczytu obecnego stanu środowiska,
- umożliwienie kontroli nad samochodami agentom,
- kontrola poprawności działania środowiska w trakcie symulacji.

Aby użytkownik mógł odpowiednio testować oraz modyfikować działanie swojego agenta, wymagane jest, by środowisko umożliwiało jednocześnie zmianę i różnicowanie parametrów startowych środowiska, ale również powtarzalność działania środowiska przy tych samych parametrach.

Użytkownik może wpływać na: 
- liczbę samochodów sterowanych przez środowisko (botów),
- liczbę punktów na mapie,
- procent skrzyżowań, na których znajdują się sygnalizacje świetlne,
- długość cykli sygnalizacji świetlnych.

Dodatkowo, użytkownik może podać **ziarno (seed)** jako liczbę, na podstawie którego tworzony jest generator liczb pseudolosowych, który odpowiada za inicjalizację środowiska oraz sterowanie botami. Daje to dwie znaczące zalety:
- użytkownik może wykorzystywać różne seedy dla tych samych parametrów startowych środowiska, aby dokładniej przetestować swojego agenta w podobnych warunkach,
- użytkownik może powtórnie wykonywać testy dla tego samego seeda, aby umożliwiść obserwację poprawy lub pogorszenia agenta w trakcie jego tworzenia i testowania.

W trakcie działania środowiska, backend sprawuje kontrolę ruchem samochodów, punktami i sygnalizacją świetlną. W każdym interwale samochody otrzymują informację o aktualnym stanie środowiska, na podstawie której deklarują akcję, którą chcą wykonać w trakcie tego interwału. Następnie środowisko sprawdza zgodność akcji z zasadami opisanymi wyżej, a następnie przemieszcza samochody, których akcje były dozwolone. Sprawdzane jest również, czy agent w trakcie swojego ruchu zebrał któryś z punktów, oraz zmienia kolor sygnalizacji świetlnej, jeżeli minął określony czas.

#### Interfejs samochodów

Zarówno samochody zarządzane przez środowisko, jak i te zarządzane przez agentów, korzystają ze wspólnego interfejsu, który w uproszczeniu przedstawia się następująco:

    class Car:
    	@abstractmethod
		def get_action(self, map_state: MapState) -> Action:
			pass
Środowisko, na początku każdego interwału, wywołuje na każdym obiekcie klasy `Car` metodę `get_action`, aby uzyskać akcje podjęte przez każdy samochód. Implementując metodę `get_action` można definiować logikę, jaką kieruje się samochód w trakcie poruszania się po mapie. Środowisko przekazuje do metody aktualny stan mapy za pomocą obiektu `MapState`, dzięki czemu samochód posiada informacje potrzebne do podjęcia pożądanej decyzji.

Samochody sterowane przez środowisko (boty) poruszają się po mapie bez żadnego celu i symulują ruch uliczny. Zachowują się w sposób pseudolosowy, przy czym ich zachowanie jest powtarzalne przy kolejnych wywołaniach środowiska z tymi samymi parametrami. Ich decyzje w jednym interwale można opisać następująco:
- jeżeli znajdujesz się przed skrzyżowaniem, wybierz jedną z dostępnych dróg aby kontynuować jazdę;
- w przeciwnym wypadku (samochód znajduje się na prostej drodze), w 95% przypadków jedź prosto, w 5% przypadków zawróć.

Boty po wybraniu kolejnej drogi przed skrzyżowaniem nie zmieniają swojej pierwotnej decyzji i będą czekały do momentu aż środowisko pozwoli im podjąć wybraną akcję. To potrafi doprowadzić do zakleszczeń na drodze, np. gdy 4 samochody dojadą równocześnie do skrzyżowania i każdy chce pojechać prosto (każdy musi ustąpić pierwszeństwa samochodowi z prawej i żaden nie potrafi jako pierwszy przejechać skrzyżowania). To zachowanie jest szerzej opisane w dalszej części raportu.

Użytkownicy implementując klasy samochodów inteligentnych agentów mogą stosować dowolne metody i algorytmy sztucznej inteligencji, a ich wynik musi być zwracany poprzez metodę `get_action`. Użytkownik następnie może przekazać swoją klasę `Car` do środowiska, by sprawdzić jego działanie.

#### Dodatkowe API dla użytkowników i dokumentacja
Klasa `MapState` zawiera w sobie wszystkie informacje o środowisku, jakich może potrzebować agent do podjęcia decyzji, lecz dla początkującego użytkownika struktura środowiska i danych wewnętrznych może okazać się przytłaczająca. Z tego powodu zaimplementowana została dodatkowo dlasa `EnvironmentAPI`, która przyjmuje do inicjalizacji obiekt `MapState` i wystawia dodatkowe metody, które mogą być przydatne użytkownikom w trakcie implementowania agentów. Przykładowe metody to:
- `is_position_road_end`,
- `get_road_length`,
- `get_points_for_specific_car`,
- `get_available_turns`.

Jeżeli jednak potrzeby użytkownika wybiegają poza przewidziane scenariusze, wszystkie klasy oraz metody **w całej bibliotece** posiadają swoją dokumentację, aby umożliwić użytkownikowi znalezienie i skorzystanie z wymaganych przez niego funkcjonalności.

Dodatkowo, w bibliotece znajdują się 2 przykłady implementacji klasy `Car`, aby wprowadzić początkowo użytkowników w implementowanie własnych agentów.

### Napotkane problemy i decyzje
W trakcie implementacji środowiska, zespół napotkał wiele problemów i dylematów, zarówno w fazie projektowania środowiska, jak i późniejszej implementacji. W tej części przedstawiono decyzje, które zostały podjęte oraz rozumowanie stojące za nimi.
#### Mapa 
Mapa środowiska przedstawiona jest jako dwuwymiarowa kwadratowa siatka składająca się z kafelków, co ogranicza sposób w jaki drogi mogą się łączyć oraz maksymalną liczbę dróg dochodzącą do skrzyżowania. W początkowych rozważaniach zespół brał pod uwagę również tworzenie mapy na podstawie grafu bez ograniczeń połączeń pomiędzy węzłami, lecz odrzucono ten pomysł ze względu na trudność w graficznym przedstawieniu takiej siatki dróg i ruchu na nich w czytelny sposób.

Brano pod uwagę również pomysł, by zamiast dyskretnych pól na drogach, pomiędzy którymi samochód w trakcie jazdy "przeskakuje", użyć modeli samochodów poruszających się po drogach w sposób "ciągły"/płynny. Znacząco to jednak skomplikowałoby stworzenie takiego środowiska oraz formę informacji o aktualnym stanie środowiska, co przekroczyłoby zakres trudności tego projektu.

Układ dróg na mapie jest stały i tworzony na podstawie pliku zawierającego układ dróg w formie tekstowej. Możliwe jest w przyszłości rozszerzenie funkcjonalności środowiska o dodanie generatora mapy, by zwiększyć różnorodność problemów.

#### Czas oraz akcje
Czas w środowisku został zaimplementowany jako dyskretne interwały, gdzie w każdym interwale samochód jest w stanie wykonać jedną akcję. Początkowo rozważano ideę, aby samochód był w stanie podjąć decyzję jedynie w momencie dojechania do skrzyżowania, lecz znacząco ograniczyłoby to możliwość działania inteligentnym agentom. Dodano również wtedy opcję zawrócenia na prostej drodze, by móc np. ominąć duży korek znajdujący się przed samochodem wybierając inną trasę.

#### Ziarno (seed)
Ze względu na to, że jest to środowisko do implementacji metod i algorytmów sztucznej inteligencji przez użytkowników, potrzebne było stworzenie odpowiednich warunków do testowania i sprawdzania postępów agentów. 

Z tego powodu uznano, że poza losowością wymaganą do stworzenia różnych scenariuszy problemów, potrzebna jest również pewna powtarzalność i przewidywalność w zachowaniu środowiska, tak aby na wypadek znalezienia jakiegoś szczególnego przypadku przez użytkownika, w którym jego agent sobie nie radzi, można było sprawdzić działanie algorytmu na tym samym przypadku po wprowadzonych zmianach. 

Problem ten rozwiązało użycie w środowisku ziarna (seeda), popularnego np. w grach komputerowych, które użytkownik może jawnie podać do środowiska, by móc wielokrotnie wykonać testy w tych samych warunkach.
#### Rozmieszczenie punktów
Samochód by zebrać punkt musi najechać na dowolne pole na kafelku drogi, lecz względu na to, że w trakcie implementacji środowiska podjęto decyzję, że samochody nigdy fizycznie nie znajdują się na skrzyżowaniu, początkowo nie uwzględniano opcji o stawianiu punktów do zebrania przez agentów na skrzyżowaniach. W późniejszej fazie uznano jednak, że może to ograniczyć kreatywne możliwości agentów do znajdywania najbardziej optymalnej ścieżki w środowisku, dlatego zdecydowano się znaleźć sposób na umieszczanie punktów na skrzyżowaniach i znalezienia sposobu na ich zbieranie przez samochody. 

Ostateczne rozwiązanie uwzględnia, że jako przejechanie przez skrzyżowanie można uznać fakt podjęcia pomyślnej akcji wybrania kolejnej drogi znajdując się przed skrzyżowaniem i do tej akcji przypisano możliwość zebrania punktu znajdującego się na skrzyżowaniu.

#### Zakleszczenia na drodze
Po zaimplementowaniu zasad ruchu drogowego, przez które samochód nie może przejechać przez skrzyżowanie, jeżeli powinien ustąpić pierwszeństwa, pojawił się problem zakleszczenia. Dzieje się tak, gdy 3 lub 4 samochody stoją przed skrzyżowaniem, a ich wybrane akcje sprawiają, że każdy samochód musi ustąpić jakiemuś innemu pierwszeństwa. Takie zakleszczenie potrafi się pojawić i sprawia, że skrzyżowanie staje się właściwie nieprzejezdne.

Początkowo problem ten miał zostać zlikwidowany, natomiast znalezienie odpowiedniego rozwiązania, które wydawałoby się naturalne w porównaniu z rzeczywistym światem, okazało się trudne, a propozycje jak np. wprowadzenie dla samochodów "miernika cierpliwości" okazało się dyskusyjne, dlatego odłożono rozwiązanie problemu w czasie. 

W momencie, gdy użytkownicy rozpoczęli tworzenie swoich agentów, okazało się, że problem ten jest dodatkowym ciekawym urozmaiceniem, który można porównać np. do karambolu na drodze, a umiejętność przewidywania takich miejsc i ich unikania okazała się cenna z punktu widzenia implementacji algorytmów. Ostatecznie zdecydowano więc nie likwidować tego zachowania w myśl zasady "it's not a bug, it's a feature".


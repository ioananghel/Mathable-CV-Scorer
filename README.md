# Mathable-CV-Scorer

Acest proiect are ca scop crearea unui sistem de analiza a tablelor de joc Mathable si urmarirea miscarilor facute de jucatori, pentru a calcula scorurile obtinute de acestia pe parcursul rundelor. Aceasta sarcina a fost impartita in trei parti: detectia unei noi piese plasate intr-o miscare, specificand indexul acesteia, identificarea numarului de pe piesa si intr-un final, calcularea scorului asociat fiecarei runde.

Sistemul creat si descris in aceasta lucrare foloseste tehnici de segmentare a imaginilor, detectare a contururilor si pattern matching pentru a indeplini aceasta sarcina.

Solutia propusa are o performanta de 100\% acuratete pe seturile de antrenare si validare, insa nu este una foarte robusta, bazandu-se pe caracterul constant al seturilor de date, in ceea ce priveste perspectiva asupra tablei, luminozitatea si zona din care vine lumina. Asadar, parametrii gasiti prin testare ar putea sa nu fie aplicabili in alte situatii.

<details>
<summary>
<h3 style="display:inline-block">Requirements</h3>
</summary>

---

 - matplotlib==3.8.3
 - opencv-python==4.9.0.80
 - numpy==1.26.4
</details>

<details>
<summary>
<h3 style="display:inline-block">Cum se ruleaza solutia</h3>
</summary>

---

- In fisierul <b>configs.py</b> se schimba variabila <b>trainDir</b> cu denumirea fisierului ce contine datele de analizat
    ```
    # configuratia curenta:
    trainDir = os.path.join(rootDir, 'antrenare')
    ```
- Se ruleaza fisierul <b>solve.py</b>
    ```
    python3 solve.py
    ```
</details>
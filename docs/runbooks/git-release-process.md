\# Git Release Process



\## Standart Akış



1\. Production test tamamlanır.

2\. Rapor ChatGPT ile analiz edilir.

3\. Milestone PASS ise docs/releases altında release notu oluşturulur.

4\. Gerekirse CHANGELOG ve PRODUCTION\_ROADMAP güncellenir.

5\. Git commit yapılır.

6\. GitHub'a push yapılır.

7\. Tag oluşturulur.



\## Komutlar



```bat

git status

git add .

git commit -m "docs: add release notes"

git push

git tag <tag-name>

git push origin <tag-name>


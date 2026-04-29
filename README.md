# Projet d'analyse de la difficulté de Super Mario Bros

Le projet suivant consiste à analyser des vidéos de personnes jouant à Super Mario Bros sur NES, afin de tirer un maximum d'informations sur les sessions de jeu dans le but d'analyser les tendances générales, comme le temps de jeu, le nombre de sauts, ou encore de morts par niveau.

Les instructions d'utilisation détaillées sont trouvables dans les README des sous dossiers

## [Analyse des vidéo](./src/)

L'analyse des vidéos est faite en python via la détection de sprites sur chaque frame.

Une ancienne version dépréciée ([audio not used](./src/audio_not-used/)) à été partiellement implémentée pour détecter certains évènements via l'audio, mais rapidement abandonnée car difficilement utilisable en pratique.

Les résultats de cette analyse sont ensuite stockés dans [data](./data/) sous forme de fichier csv.

## [Application de visualisation des données](./shiny/)

Le résultat des analyses peut être observé dans une application web shiny développée en Python.

Voir le [Shiny README](./shiny/README.md)

## Prérequis

* Python3

## Crédits

Les sprites utilisés pour les templates sont tirés de Super Mario Bros sur NES, et obtenus via *[The Spriters Resource](https://www.spriters-resource.com/nes/supermariobros/)*

## MIT Licence

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the " Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice (including the next paragraph) shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

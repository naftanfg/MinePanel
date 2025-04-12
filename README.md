# Gestione Server Minecraft - Guida (Italiano)

Questa applicazione Flask permette di gestire versioni di server Minecraft.

## Requisiti

- Python 3
- `pip install flask`

## Avvio

Per avviare il sito:

```bash
python app.py
```

Il sito sarà disponibile su `http://localhost:5070`

## Funzioni

- Homepage: mostra tutte le versioni Minecraft salvate
- Aggiungi: permette di aggiungere una nuova versione
- Gestione server:
  - Scarica: scarica il file `.jar` dal link salvato
  - Avvia: avvia il server con Java
  - Riavvia: riavvia il server
  - Stop: arresta il server
  - Elimina: rimuove la versione dal database

## Aggiunta Versione

Esempio da usare:

- Nome: `1.20.4`
- Link: `https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar`

Puoi cercare altre versioni qui:  
👉 https://jars.vexyhost.com/

## Cartelle

I file dei server vengono salvati in `./server-file/<versione>`

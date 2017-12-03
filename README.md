# infokello
Kellonajan ja FMI sääinfon näyttäjä raspberry pi SenseHat alustalle

# Toiminta
Näyttää loopissa kellonajan, lämpötilan, tuulennopeuden ja
sisäilman paineen SenseHat alustalle vierivänä tekstinä.

# Käyttöönotto
1. Rekisteröidy [FMI api käyttäjäksi](https://ilmatieteenlaitos.fi/rekisteroityminen-avoimen-datan-kayttajaksi)
2. Täydennä config.json api avaimella jonka saat ilmaiseksi FMI:ltä
3. vaihda config.json tiedostoon haluamasi säätiedon sijainti
4. käynnistä sovellus: `python3 infokello.py`

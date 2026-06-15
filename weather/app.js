const input = document.getElementById('cityInput');
const btn = document.getElementById('searchBtn');

function getWeather(city) {
  const url = `https://wttr.in/${encodeURIComponent(city)}?format=j1`;
  fetch(url)
    .then(res => res.json())
    .then(data => {
      const cur = data.current_condition[0];
      const weatherDesc = cur.weatherDesc[0].value;
      const temp = cur.temp_C;
      const feels = cur.FeelsLikeC;
      const humidity = cur.humidity;
      const wind = cur.windspeedKmph;

      alert(`🌤️ ${city}\n${weatherDesc}\nSuhu: ${temp}°C\nTerasa: ${feels}°C\nKelembaban: ${humidity}%\nAngin: ${wind} km/h`);
    })
    .catch(() => alert('Gagal mengambil data cuaca.'));
}

btn.addEventListener('click', () => {
  const city = input.value.trim();
  if (city) getWeather(city);
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') btn.click();
});

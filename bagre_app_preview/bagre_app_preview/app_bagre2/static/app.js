// Registro de watch >= 3s, likes e comentários
async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  return await res.json();
}

function attachWatchObserver(videoId) {
  let watched = 0;
  let lastVisible = null;
  const el = document.getElementById(videoId);
  if (!el) return;

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        lastVisible = Date.now();
      } else if (lastVisible) {
        watched += (Date.now() - lastVisible) / 1000.0;
        lastVisible = null;
        if (watched >= 3) {
          postJSON('/api/watch', { video_id: videoId, seconds: Math.round(watched) });
          // only trigger once
          watched = -999;
        }
      }
    });
  }, { threshold: 0.5 });

  obs.observe(el);
}

function likeVideo(videoId) {
  postJSON('/api/like', { video_id: videoId }).then(r => {
    alert('Like registrado: ' + videoId);
  });
}

function commentVideo(videoId) {
  const comment = prompt('Digite seu comentário:');
  if (!comment) return;
  postJSON('/api/comment', { video_id: videoId, comment }).then(r => {
    alert('Comentário salvo localmente.');
  });
}

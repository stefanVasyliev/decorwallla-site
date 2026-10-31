// Shared behaviour for every page: header on scroll, mobile menu, reveal on scroll, WhatsApp link.
// Every page opens at the top unless the link points at a section (#...).
// When the site is shown inside another page (a preview frame), the outer page is scrolled too.
if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
const toTop = () => {
  if (location.hash) return;
  window.scrollTo(0, 0);
  try { document.documentElement.scrollIntoView({ block: 'start', behavior: 'instant' }); } catch (e) { document.documentElement.scrollIntoView(true); }
};
toTop();
window.addEventListener('pageshow', toTop);
window.addEventListener('load', toTop);

(() => {
  const header = document.querySelector('[data-header]');
  // On the home page the walls change while the hero stays put; the backdrop waits until the page moves on.
  const track = document.querySelector('[data-track]');
  const threshold = () => (track ? track.offsetTop + track.offsetHeight - window.innerHeight + 40 : 40);
  const onScroll = () => header && header.classList.toggle('is-scrolled', window.scrollY > threshold());
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const burger = document.querySelector('[data-burger]');
  const menu = document.querySelector('[data-menu]');
  if (burger && menu && !burger.dataset.bound) {
    burger.dataset.bound = '1';
    const setMenu = (open) => {
      burger.setAttribute('aria-expanded', String(open));
      document.body.classList.toggle('menu-open', open);
      menu.hidden = !open;
    };
    burger.addEventListener('click', () => setMenu(menu.hidden));
    menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => setMenu(false)));
  }

  if (!window.__revealBound) {
    const io = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -10% 0px' });
    document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
  }

  // WhatsApp: the number is set once, on <body data-whatsapp>, by the site generator.
  const num = document.body.dataset.whatsapp || '';
  document.querySelectorAll('[data-wa]').forEach((wa) => {
    const text = wa.classList.contains('btn-wa') ? 'Hi DecorWall! I would like a free design preview for my wall.' : 'Hi DecorWall! I have a question about a wall.';
    wa.href = `https://wa.me/${num}?text=${encodeURIComponent(text)}`;
  });

  // Keep UTM tags with form submissions.
  const params = new URLSearchParams(location.search);
  document.querySelectorAll('[data-utm]').forEach((el) => { el.value = params.get(el.dataset.utm) || ''; });
})();

// Estimate form: the photo chip shows how many photos were added.
document.querySelectorAll('[data-file]').forEach((wrap) => {
  const input = wrap.querySelector('input');
  const label = wrap.querySelector('[data-file-label]');
  input.addEventListener('change', () => {
    const n = input.files.length;
    wrap.classList.toggle('has-files', n > 0);
    label.textContent = n ? `${n} photo${n > 1 ? 's' : ''} added` : 'Add photos';
  });
});

// Dark sections get a hidden LED line that lights up as they come into view; each sits in a different place.
(() => {
  const spots = [['8%', '34%'], ['54%', '38%'], ['26%', '30%'], ['60%', '28%'], ['14%', '44%']];
  const dark = [...document.querySelectorAll('main > section, footer.foot')].filter((el) =>
    !el.classList.contains('paper') && !el.classList.contains('hero') && !el.classList.contains('why') && !el.closest('.track'));
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('lit'); io.unobserve(e.target); }
  }), { threshold: 0.15 });
  dark.forEach((el, i) => {
    const [x, w] = spots[i % spots.length];
    el.classList.add('glow');
    el.style.setProperty('--gx', x);
    el.style.setProperty('--gw', w);
    io.observe(el);
  });
})();

// What we build: pointing at or clicking a name shows that wall; the link on the photo opens its page.
document.querySelectorAll('.idx').forEach((idx) => {
  const items = idx.querySelectorAll('[data-idx-item]');
  const pics = idx.querySelectorAll('[data-idx-pic]');
  const rows = idx.querySelectorAll('[data-idx-row]');
  const show = (k) => {
    items.forEach((x) => { const on = x.dataset.idxItem === k; x.classList.toggle('is-on', on); x.setAttribute('aria-pressed', String(on)); });
    rows.forEach((r) => r.classList.toggle('is-on', r.dataset.idxRow === k));
    pics.forEach((p) => p.classList.toggle('is-on', p.dataset.idxPic === k));
  };
  rows.forEach((r) => r.addEventListener('mouseenter', () => show(r.dataset.idxRow)));
  items.forEach((btn) => btn.addEventListener('click', () => show(btn.dataset.idxItem)));
});



// Inner pages: the page moves with a little weight, slows as each section arrives, and settles
// onto a section edge when scrolling stops close to it. (The home page has its own version.)
(() => {
  if (document.querySelector('[data-track]') || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const SMOOTH = 0.07, BRAKE = 0.22, ZONE = 0.55, SNAP = 0.4, SNAP_AFTER = 160;
  let pos = window.scrollY, target = pos, gliding = false, last = 0, timer = 0;
  const max = () => document.documentElement.scrollHeight - window.innerHeight;
  const tops = () => [...document.querySelectorAll('main > section, footer')].map((el) => el.offsetTop).filter((t) => t > 0);
  const nearest = (y) => tops().reduce((b, t) => (b === null || Math.abs(t - y) < Math.abs(b - y) ? t : b), null);
  const brake = (y) => {
    const t = nearest(y); if (t === null) return 1;
    const d = Math.abs(y - t) / (window.innerHeight * ZONE);
    return d >= 1 ? 1 : BRAKE + (1 - BRAKE) * d * d * (3 - 2 * d);
  };
  const glide = (now) => {
    const dt = last ? Math.min((now - last) / 16.67, 4) : 1; last = now;
    pos += (target - pos) * (1 - Math.pow(1 - SMOOTH, dt));
    if (Math.abs(target - pos) < 0.5) { pos = target; gliding = false; }
    window.scrollTo(0, pos);
    if (gliding) requestAnimationFrame(glide);
  };
  const to = (y) => {
    target = Math.min(Math.max(y, 0), max());
    if (!gliding) { gliding = true; pos = window.scrollY; last = 0; requestAnimationFrame(glide); }
  };
  let dir = 1;
  // Only pull towards an edge that is ahead in the direction of travel, never back to one just left.
  const snap = () => { const t = nearest(target); if (t !== null && (dir > 0 ? t > target : t < target) && Math.abs(t - target) > 1 && Math.abs(t - target) < window.innerHeight * SNAP) to(t); };
  window.addEventListener('wheel', (e) => {
    if (e.ctrlKey || document.body.classList.contains('menu-open')) return;
    e.preventDefault();
    const unit = e.deltaMode === 1 ? 40 : e.deltaMode === 2 ? window.innerHeight : 1;
    const from = gliding ? target : window.scrollY;
    if (e.deltaY) dir = Math.sign(e.deltaY);
    to(from + e.deltaY * unit * brake(from));
    clearTimeout(timer); timer = setTimeout(snap, SNAP_AFTER);
  }, { passive: false });
  window.addEventListener('scroll', () => { if (!gliding) pos = target = window.scrollY; }, { passive: true });
})();


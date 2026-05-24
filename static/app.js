async function loadArticles() {
  const list = document.getElementById("article-list");

  try {
    const res = await fetch(`/articles`, { method: "GET" });
    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    const data = await res.json();

    const sorted = Object.values(data).sort(
      (a, b) => new Date(b.upload_date) - new Date(a.upload_date),
    );

    if (sorted.length === 0) {
      list.innerHTML = '<p class="status-text">No articles found.</p>';
      return;
    }

    list.innerHTML = "";

    sorted.forEach((article, index) => {
      const date = new Date(article.upload_date).toLocaleDateString("en-GB", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });

      const item = document.createElement("div");
      item.className = "article-item";
      item.dataset.id = article.title;
      item.style.animationDelay = `${index * 55}ms`;
      item.innerHTML = `
        <div class="article-item-title">${escHtml(article.title)}</div>
        <div class="article-item-date">${date}</div>
      `;
      item.addEventListener("click", () => openArticle(article.title, item));
      list.appendChild(item);

      if (index === 0) openArticle(article.title, item);
    });
  } catch (err) {
    list.innerHTML = `<p class="status-text">⚠ ${escHtml(err.message)}</p>`;
    console.error("[articles]", err);
  }
}

function openArticle(id, itemEl) {
  document
    .querySelectorAll(".article-item")
    .forEach((el) => el.classList.remove("active"));
  if (itemEl) itemEl.classList.add("active");
  document.getElementById("article-frame").src =
    `/article/${base64URLencode(id)}`;
}

function base64URLencode(str) {
  const base64Encoded = btoa(str);
  return base64Encoded
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", loadArticles);

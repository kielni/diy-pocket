function articlesApp() {
  return {
    articles: [],
    loading: true,
    selectedTag: "",
    allTags: [],
    tagCounts: {},
    drawPartial() {
      this.showPartial = true;
      setTimeout(() => {
        this.showPartial = false;
      }, 100);
    },
    clearTagFilter() {
      this.selectedTag = "";
      this.tagSearch = "";
      this.drawPartial();
    },
    filteredArticles() {
      const list = this.selectedTag
        ? this.articles.filter(
            (a) => a.tags && a.tags.includes(this.selectedTag)
          )
        : this.articles;
      return this.showPartial ? list.slice(0, 12) : list;
    },
    async loadArticles() {
      try {
        const response = await fetch(DATA_URL);
        let data = await response.json();
        const tagSet = new Set();
        const tagCounts = {};
        data.forEach((article) => {
          article.displayDate = article.timestamp
            ? new Date(article.timestamp).toLocaleDateString("en-US", {
                year: "2-digit",
                month: "numeric",
                day: "numeric",
              })
            : "";
          if (!article.title || !article.title.trim()) {
            article.title = article.url
              .replace(/\/$/, "")
              .split("/")
              .pop()
              .replace(/-/g, " ");
          }
          if (article.tags && Array.isArray(article.tags)) {
            article.tags.forEach((tag) => {
              tagSet.add(tag);
              tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
          }
        });
        data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        this.articles = data;
        this.allTags = Array.from(tagSet).sort();
        this.tagCounts = tagCounts;
        this.drawPartial();
      } catch (e) {
        this.articles = [];
        this.allTags = [];
        this.tagCounts = {};
      } finally {
        this.loading = false;
      }
    },
  };
}

document.addEventListener("alpine:init", () => {
  window.articlesAppInstance = Alpine.store("articlesApp") || null;
});

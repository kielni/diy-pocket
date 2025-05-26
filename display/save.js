function saveArticleApp() {
  return {
    url: "",
    title: "",
    source: "",
    excerpt: "",
    tags: "",
    photo_url: "",
    loading: false,
    success: false,
    error: "",
    async submit() {
      this.loading = true;
      this.success = false;
      this.error = "";
      try {
        const payload = {
          url: this.url,
          title: this.title,
          source: this.source,
          excerpt: this.excerpt,
          tags: this.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          photo_url: this.photo_url,
        };
        const response = await fetch(SAVE_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-auth-token": AUTH_TOKEN,
          },
          body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (response.ok) {
          this.success = true;
          this.url =
            this.title =
            this.source =
            this.excerpt =
            this.tags =
            this.photo_url =
              "";
        } else {
          console.error("Error saving article:", result);
          this.error = result.error || "Error saving article";
        }
      } catch (err) {
        this.error = "Network error";
      } finally {
        this.loading = false;
      }
    },
  };
}

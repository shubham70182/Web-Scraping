/**
 * ScrapeFlow Studio - Simple & Clean Frontend Logic
 * Beginner-friendly vanilla JavaScript using async/await and standard fetch().
 */

document.addEventListener("DOMContentLoaded", () => {
  // --- 1. Tab Navigation ---
  const tabButtons = document.querySelectorAll(".nav-tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      // Update active button and pane
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const activePane = document.getElementById(targetTab);
      if (activePane) activePane.classList.add("active");

      // Load data when switching tabs
      if (targetTab === "tab-crud") {
        loadRecords();
      } else if (targetTab === "tab-schema") {
        loadDatabaseSchema();
      }
    });
  });

  // --- 2. Database Health & Status Check ---
  async function checkDatabaseHealth() {
    try {
      const response = await fetch("/api/health");
      const data = await response.json();
      const dot = document.getElementById("engineDot");
      const text = document.getElementById("engineStatusText");

      if (data.database && data.database.is_postgresql_connected) {
        dot.className = "status-dot";
        text.textContent = "PostgreSQL Connected (Live)";
      } else {
        dot.className = "status-dot fallback";
        text.textContent = "SQLite Local Mode";
      }
    } catch (err) {
      console.error("Health check error:", err);
    }
  }
  checkDatabaseHealth();

  // --- 3. Quick URL Presets ---
  document.querySelectorAll(".pill-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const url = btn.getAttribute("data-url");
      document.getElementById("targetUrlInput").value = url;
    });
  });

  // --- 4. Detect Dynamic Website ---
  const btnDetect = document.getElementById("btnDetect");
  btnDetect.addEventListener("click", async () => {
    const url = document.getElementById("targetUrlInput").value.trim();
    if (!url) return alert("Please enter a valid website URL.");

    const spinner = document.getElementById("detectSpinner");
    spinner.style.display = "inline-block";

    try {
      const response = await fetch(`/api/detect-dynamic?url=${encodeURIComponent(url)}`);
      const data = await response.json();

      // Show diagnosis card
      const diagCard = document.getElementById("dynamicDiagCard");
      diagCard.classList.add("active");

      const badge = document.getElementById("diagBadge");
      badge.textContent = data.is_dynamic ? "DYNAMIC (JS Rendered)" : "STATIC (HTML Pre-rendered)";
      badge.className = `diag-score-badge ${data.is_dynamic ? "high" : "low"}`;

      document.getElementById("diagScoreText").textContent = `Dynamic Score: ${data.confidence_score || 0}/10`;

      // Tech tags
      const techContainer = document.getElementById("diagTechTags");
      techContainer.innerHTML = (data.detected_tech || []).map(t => `<span class="tech-tag">${t}</span>`).join("");

      // Reasons list
      const reasonsList = document.getElementById("diagReasonsList");
      reasonsList.innerHTML = (data.reasons || []).map(r => `<li>${r}</li>`).join("");
    } catch (err) {
      alert("Error analyzing website: " + err.message);
    } finally {
      spinner.style.display = "none";
    }
  });

  // --- 5. Scrape & Store to PostgreSQL ---
  const scrapeForm = document.getElementById("scrapeForm");
  scrapeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = document.getElementById("targetUrlInput").value.trim();
    const maxItems = parseInt(document.getElementById("maxItemsSelect").value) || 10;

    const spinner = document.getElementById("scrapeSpinner");
    const btnScrape = document.getElementById("btnScrape");
    spinner.style.display = "inline-block";
    btnScrape.disabled = true;

    try {
      const response = await fetch("/api/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url, max_items: maxItems })
      });
      const data = await response.json();

      if (!data.success) {
        alert(data.message || "Failed to scrape website.");
        return;
      }

      // Render scraped items
      const resultsSection = document.getElementById("scrapeResultsSection");
      const grid = document.getElementById("scrapedItemsGrid");
      resultsSection.style.display = "block";

      document.getElementById("resultCount").textContent = data.count || data.items.length;
      document.getElementById("strategyBadge").textContent = `Strategy: ${data.strategy_used}`;

      grid.innerHTML = (data.items || []).map(item => `
        <div class="item-card">
          <div class="item-card-header">
            <span class="item-type-badge">${item.item_type || "item"}</span>
            <span class="item-id">ID: #${item.id || "New"}</span>
          </div>
          <div class="item-card-title">${item.title || "No Title"}</div>
          <div class="item-card-desc">${item.description || "No Description"}</div>
          <div class="item-card-meta">
            <span>🌐 ${new URL(item.source_url).hostname}</span>
            <span>📅 ${item.scraped_at ? item.scraped_at.substring(0, 10) : "Just now"}</span>
          </div>
        </div>
      `).join("");

      // Smooth scroll down to results
      resultsSection.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      alert("Scraping error: " + err.message);
    } finally {
      spinner.style.display = "none";
      btnScrape.disabled = false;
    }
  });

  // --- 6. Stored Records & CRUD Operations ---
  let currentOffset = 0;
  const pageLimit = 12;

  async function loadRecords() {
    const search = document.getElementById("crudSearchInput").value.trim();
    const urlFilter = document.getElementById("crudUrlFilter").value.trim();
    const typeFilter = document.getElementById("crudTypeFilter").value.trim();

    let url = `/api/items?limit=${pageLimit}&offset=${currentOffset}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (urlFilter) url += `&source_url=${encodeURIComponent(urlFilter)}`;
    if (typeFilter) url += `&item_type=${encodeURIComponent(typeFilter)}`;

    try {
      const response = await fetch(url);
      const data = await response.json();

      document.getElementById("crudDisplayCount").textContent = data.items.length;
      document.getElementById("crudTotalCount").textContent = data.total;

      const grid = document.getElementById("crudItemsGrid");
      if (!data.items || data.items.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 3rem;">No stored records found. Try scraping a website first!</div>`;
        return;
      }

      grid.innerHTML = data.items.map(item => `
        <div class="item-card">
          <div class="item-card-header">
            <span class="item-type-badge">${item.item_type || "item"}</span>
            <span class="item-id">ID: #${item.id}</span>
          </div>
          <div class="item-card-title">${item.title || "Untitled"}</div>
          <div class="item-card-desc">${item.description || "No description provided."}</div>
          <div class="item-card-meta">
            <span title="${item.source_url}">🌐 ${item.source_url.length > 25 ? item.source_url.substring(0, 25) + '...' : item.source_url}</span>
            <span>📅 ${item.scraped_at ? item.scraped_at.substring(0, 10) : "N/A"}</span>
          </div>
          <div class="card-actions">
            <button class="btn-action edit" onclick="window.openEditModal(${item.id}, ${JSON.stringify(item.title).replace(/"/g, '&quot;')}, ${JSON.stringify(item.description || '').replace(/"/g, '&quot;')})">✏️ Edit</button>
            <button class="btn-action delete" onclick="window.deleteRecord(${item.id})">🗑️ Delete</button>
          </div>
        </div>
      `).join("");
    } catch (err) {
      console.error("Error loading records:", err);
    }
  }

  // Filter triggers
  document.getElementById("crudSearchInput").addEventListener("input", () => { currentOffset = 0; loadRecords(); });
  document.getElementById("crudUrlFilter").addEventListener("input", () => { currentOffset = 0; loadRecords(); });
  document.getElementById("crudTypeFilter").addEventListener("change", () => { currentOffset = 0; loadRecords(); });
  // Handle Refresh CRUD with visual feedback
  window.handleRefreshCrud = async function(btn) {
    if (!btn) btn = document.getElementById("btnRefreshCrud");
    const origHtml = btn ? btn.innerHTML : "🔄 Refresh";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `🔄 Refreshing...`;
    }
    try {
      await loadRecords();
      if (btn) {
        btn.innerHTML = `✅ Refreshed!`;
        setTimeout(() => {
          btn.innerHTML = origHtml;
          btn.disabled = false;
        }, 1000);
      }
    } catch (err) {
      console.error("Refresh error:", err);
      if (btn) {
        btn.innerHTML = origHtml;
        btn.disabled = false;
      }
    }
  };

  // Handle Clear All Records
  window.handleClearAllRecords = async function(btn) {
    if (!btn) btn = document.getElementById("btnClearAllRecords");
    const confirmed = confirm(
      "⚠️ DANGER: Are you sure you want to delete ALL records from the database?\n\nThis will permanently delete all stored data and reset the ID sequence back to 1."
    );
    if (!confirmed) return;

    const origHtml = btn ? btn.innerHTML : "🗑️ Clear All";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `⏳ Clearing...`;
    }

    try {
      const response = await fetch("/api/items", { method: "DELETE" });
      const data = await response.json();
      if (response.ok && data.success) {
        currentOffset = 0;
        await loadRecords();
        alert("✅ All records successfully deleted from the database!");
      } else {
        alert("Failed to delete records: " + (data.message || response.statusText));
      }
    } catch (err) {
      alert("Error clearing database: " + err.message);
    } finally {
      if (btn) {
        btn.innerHTML = origHtml;
        btn.disabled = false;
      }
    }
  };

  const btnRefreshCrud = document.getElementById("btnRefreshCrud");
  if (btnRefreshCrud) {
    btnRefreshCrud.addEventListener("click", () => window.handleRefreshCrud(btnRefreshCrud));
  }

  const btnClearAll = document.getElementById("btnClearAllRecords");
  if (btnClearAll) {
    btnClearAll.addEventListener("click", () => window.handleClearAllRecords(btnClearAll));
  }

  // Pagination
  document.getElementById("btnPrevPage").addEventListener("click", () => {
    if (currentOffset >= pageLimit) {
      currentOffset -= pageLimit;
      loadRecords();
    }
  });
  document.getElementById("btnNextPage").addEventListener("click", () => {
    currentOffset += pageLimit;
    loadRecords();
  });

  // Delete Record
  window.deleteRecord = async function(id) {
    if (!confirm(`Are you sure you want to delete record #${id}?`)) return;
    try {
      const response = await fetch(`/api/items/${id}`, { method: "DELETE" });
      if (response.ok) {
        loadRecords();
      } else {
        alert("Failed to delete record.");
      }
    } catch (err) {
      alert("Error deleting record: " + err.message);
    }
  };

  // Edit Modal Setup
  const editModal = document.getElementById("editModal");
  window.openEditModal = function(id, title, desc) {
    document.getElementById("editItemId").value = id;
    document.getElementById("editTitleInput").value = title || "";
    document.getElementById("editDescInput").value = desc || "";
    editModal.classList.add("active");
  };

  document.getElementById("editForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("editItemId").value;
    const title = document.getElementById("editTitleInput").value;
    const desc = document.getElementById("editDescInput").value;

    try {
      const response = await fetch(`/api/items/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title, description: desc })
      });
      if (response.ok) {
        editModal.classList.remove("active");
        loadRecords();
      } else {
        alert("Failed to update record.");
      }
    } catch (err) {
      alert("Error updating record: " + err.message);
    }
  });

  // Create Modal Setup
  const createModal = document.getElementById("createModal");
  document.getElementById("btnOpenCreateModal").addEventListener("click", () => {
    createModal.classList.add("active");
  });

  document.getElementById("createForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = document.getElementById("createUrlInput").value;
    const title = document.getElementById("createTitleInput").value;
    const desc = document.getElementById("createDescInput").value;
    const itemType = document.getElementById("createTypeInput").value;

    try {
      const response = await fetch("/api/items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_url: url,
          title: title,
          description: desc,
          item_type: itemType
        })
      });
      if (response.ok) {
        createModal.classList.remove("active");
        document.getElementById("createForm").reset();
        loadRecords();
      } else {
        alert("Failed to create record.");
      }
    } catch (err) {
      alert("Error creating record: " + err.message);
    }
  });

  // Close modals when clicking cancel or outside
  document.querySelectorAll(".btn-modal-close, .modal-backdrop").forEach(el => {
    el.addEventListener("click", () => {
      editModal.classList.remove("active");
      createModal.classList.remove("active");
    });
  });

  // --- 7. Database Schema Introspection ---
  async function loadDatabaseSchema() {
    const container = document.getElementById("schemaTablesContainer");
    try {
      const response = await fetch("/api/schema");
      const data = await response.json();

      container.innerHTML = `
        <div class="schema-card">
          <div class="schema-card-header">
            <span class="schema-table-name">Table: scraped_items</span>
            <span class="item-type-badge">${data.columns.length} Columns</span>
          </div>
          <table class="schema-table">
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Data Type</th>
                <th>Nullable</th>
                <th>Default Expression</th>
              </tr>
            </thead>
            <tbody>
              ${data.columns.map(col => `
                <tr>
                  <td><strong>${col.column_name}</strong></td>
                  <td><code>${col.data_type}</code></td>
                  <td>${col.is_nullable === "YES" ? '<span style="color: #34d399;">NULL</span>' : '<span style="color: #f87171;">NOT NULL</span>'}</td>
                  <td><code>${col.default_value || 'None'}</code></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
    } catch (err) {
      container.innerHTML = `<div style="color: red; padding: 2rem;">Error fetching schema: ${err.message}</div>`;
    }
  }
});

// Ovees Eleganza Admin Dashboard - Modern UI with Modal-based Create/Edit
const token = () => localStorage.getItem('ovees_admin_token') || '';

async function api(path, opts = {}) {
  const headers = opts.headers || {};
  if (token()) headers['Authorization'] = 'Bearer ' + token();
  const res = await fetch(path, { ...opts, headers });
  if (res.status === 401) {
    window.location.href = '/admin/login';
    throw new Error('Unauthorized');
  }
  return res.json();
}

// Navigation handling
document.querySelectorAll('.nav-item').forEach(a => {
  a.addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('.nav-item').forEach(x => x.classList.remove('active'));
    a.classList.add('active');
    const section = a.getAttribute('data-section');
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById(section)?.classList.add('active');
    
    // Close mobile menu
    closeMobileMenu();
    // Refresh content for the activated section so UI shows latest data
    if (section === 'categories') loadCategories();
    else if (section === 'products') loadProducts();
    else if (section === 'banners') loadBanners();
    else if (section === 'combos') loadCombos();
    else if (section === 'new-arrivals') loadNewArrivals();
  });
});

// Mobile menu toggle: ensure body scrolling is locked when drawer is open
const _menuToggle = document.getElementById('menuToggle');
_menuToggle?.addEventListener('click', () => {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobileOverlay');
  if (!sidebar || !overlay) return;
  const opening = !sidebar.classList.contains('open');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('active');
  // lock background scroll when open on mobile
  document.body.style.overflow = opening ? 'hidden' : 'auto';
});

document.getElementById('mobileOverlay')?.addEventListener('click', closeMobileMenu);

function closeMobileMenu() {
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('mobileOverlay')?.classList.remove('active');
  document.body.style.overflow = 'auto';
}

// Logout
document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
  e.preventDefault();
  localStorage.removeItem('ovees_admin_token');
  window.location.href = '/admin/login';
});

// Modal Functions
function showModal(title, content) {
  document.getElementById('modalTitle').innerHTML = title;
  document.getElementById('modalBody').innerHTML = content;
  document.getElementById('modalContainer').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modalContainer').classList.remove('active');
  document.body.style.overflow = 'auto';
}

// Close modal on outside click
document.getElementById('modalContainer')?.addEventListener('click', (e) => {
  if (e.target.id === 'modalContainer') closeModal();
});

// Dashboard Stats
async function loadStats() {
  try {
    const stats = await api('/stats/products-count');
    const container = document.getElementById('statsCards');
    container.innerHTML = '';
    const items = [
      { title: 'Total Products', value: stats.total_products, icon: 'fa-box', color: '#b8326c' },
      { title: '99 Store', value: stats['99_store'], icon: 'fa-tag', color: '#27ae60' },
      { title: '199 Store', value: stats['199_store'], icon: 'fa-tags', color: '#3498db' },
      { title: 'Combos', value: stats.combos, icon: 'fa-layer-group', color: '#f39c12' },
      { title: 'New Arrivals', value: stats.new_arrivals, icon: 'fa-star', color: '#9b59b6' }
    ];
    items.forEach(it => {
      const div = document.createElement('div');
      div.className = 'stat-card';
      div.innerHTML = `
        <h3 style="color: ${it.color}">${it.value ?? 0}</h3>
        <div class="muted"><i class="fas ${it.icon}"></i> ${it.title}</div>
      `;
      container.appendChild(div);
    });
  } catch (e) {
    console.error(e);
  }
}

// Categories
async function loadCategories() {
  try {
    const categories = await api('/categories');
    const grid = document.getElementById('categoriesList');
    grid.innerHTML = '';

    categories.forEach(c => {
      const card = document.createElement('div');
      card.className = 'item-card';

      const content = document.createElement('div');
      content.className = 'item-content';

      const title = document.createElement('h3');
      title.className = 'item-title';
      if (c.icon_url) {
        const img = document.createElement('img');
        img.src = c.icon_url;
        img.alt = c.name || 'icon';
        img.style.width = '36px'; img.style.height = '36px'; img.style.objectFit = 'cover'; img.style.borderRadius = '6px'; img.style.marginRight = '8px';
        title.appendChild(img);
      } else {
        const icon = document.createElement('i'); icon.className = 'fas fa-tag';
        title.appendChild(icon);
      }
      const textNode = document.createTextNode(' ' + (c.name || 'Untitled'));
      title.appendChild(textNode);

      const meta = document.createElement('div');
      meta.className = 'item-meta';
      if (c.description) {
        const desc = document.createElement('span');
        desc.textContent = c.description;
        meta.appendChild(desc);
      }
      const idSpan = document.createElement('span');
      idSpan.className = 'muted small';
      idSpan.textContent = 'ID: ' + c.id;
      meta.appendChild(idSpan);

      const actions = document.createElement('div');
      actions.className = 'item-actions';

      const editBtn = document.createElement('button');
      editBtn.className = 'btn btn-primary';
      editBtn.innerHTML = '<i class="fas fa-edit"></i> Edit';
  editBtn.addEventListener('click', () => editCategory(c.id, c.name || '', c.description || '', c.icon_url || ''));

      const delBtn = document.createElement('button');
      delBtn.className = 'btn btn-danger';
      delBtn.innerHTML = '<i class="fas fa-trash"></i> Delete';
      delBtn.addEventListener('click', () => deleteCategory(c.id));

      actions.appendChild(editBtn);
      actions.appendChild(delBtn);

      content.appendChild(title);
      content.appendChild(meta);
      content.appendChild(actions);

      card.appendChild(content);
      grid.appendChild(card);
    });
  } catch (e) {
    console.error(e);
  }
}

function showCreateCategory() {
  const content = `
    <form id="categoryForm" onsubmit="submitCategory(event)">
      <div class="form-group">
        <label><i class="fas fa-tag"></i> Category Name *</label>
        <input type="text" name="name" required placeholder="Enter category name">
      </div>
      <div class="form-group">
        <label><i class="fas fa-align-left"></i> Description</label>
        <textarea name="description" placeholder="Enter category description"></textarea>
      </div>
          <div class="form-group">
            <label><i class="fas fa-image"></i> Icon (optional)</label>
            <input type="file" name="icon" accept="image/*" onchange="previewImages(event, 'categoryIconPreview')">
            <div id="categoryIconPreview" class="image-preview-container"></div>
          </div>
      <div class="form-actions">
        <button type="button" class="btn" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">
          <i class="fas fa-plus"></i> Create Category
        </button>
      </div>
    </form>
  `;
  showModal('<i class="fas fa-folder-plus"></i> Create New Category', content);
}

function editCategory(id, name, description, icon_url) {
  // Build form elements to avoid string interpolation issues with quotes
  const form = document.createElement('form');
  form.id = 'categoryForm';
  form.addEventListener('submit', (e) => updateCategory(e, id));

  const fg1 = document.createElement('div'); fg1.className = 'form-group';
  const label1 = document.createElement('label'); label1.innerHTML = '<i class="fas fa-tag"></i> Category Name *';
  const input = document.createElement('input'); input.type = 'text'; input.name = 'name'; input.required = true; input.value = name;
  fg1.appendChild(label1); fg1.appendChild(input);
  const fg3 = document.createElement('div'); fg3.className = 'form-group';
  const label3 = document.createElement('label'); label3.innerHTML = '<i class="fas fa-image"></i> Icon (optional)';
  const fileInput = document.createElement('input'); fileInput.type = 'file'; fileInput.name = 'icon'; fileInput.accept = 'image/*';
  fileInput.addEventListener('change', (e) => previewImages(e, 'editCategoryIconPreview'));
  const previewDiv = document.createElement('div'); previewDiv.id = 'editCategoryIconPreview'; previewDiv.className = 'image-preview-container';
  fg3.appendChild(label3); fg3.appendChild(fileInput); fg3.appendChild(previewDiv);
  const fg2 = document.createElement('div'); fg2.className = 'form-group';
  const label2 = document.createElement('label'); label2.innerHTML = '<i class="fas fa-align-left"></i> Description';
  const textarea = document.createElement('textarea'); textarea.name = 'description'; textarea.textContent = description || '';
  fg2.appendChild(label2); fg2.appendChild(textarea);

  const actions = document.createElement('div'); actions.className = 'form-actions';
  const cancelBtn = document.createElement('button'); cancelBtn.type = 'button'; cancelBtn.className = 'btn'; cancelBtn.textContent = 'Cancel'; cancelBtn.addEventListener('click', closeModal);
  const saveBtn = document.createElement('button'); saveBtn.type = 'submit'; saveBtn.className = 'btn btn-primary'; saveBtn.innerHTML = '<i class="fas fa-save"></i> Update Category';
  actions.appendChild(cancelBtn); actions.appendChild(saveBtn);

  form.appendChild(fg1); form.appendChild(fg2); form.appendChild(fg3); form.appendChild(actions);

  showModal('<i class="fas fa-edit"></i> Edit Category', '');
  const modalBody = document.getElementById('modalBody');
  modalBody.innerHTML = ''; // ensure empty
  modalBody.appendChild(form);
  // If an icon_url was provided, show it in the preview container
  if (icon_url) {
    const preview = document.createElement('div');
    preview.className = 'image-preview';
    preview.setAttribute('data-existing-url', icon_url);
    preview.innerHTML = `
      <img src="${icon_url}" alt="icon">
      <button type="button" class="image-preview-remove" onclick="removeExistingImage(this)">
        <i class="fas fa-times"></i>
      </button>
    `;
    previewDiv.appendChild(preview);
  }
}

async function submitCategory(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData();
  formData.append('name', form.name.value);
  formData.append('description', form.description.value || '');
  const iconFile = form.icon?.files && form.icon.files[0];
  if (iconFile) formData.append('icon', iconFile);
  // If user removed existing icon, include that flag
  if (form.remove_icon && form.remove_icon.value === 'true') {
    formData.append('remove_icon', 'true');
  }
  try {
  const btn = form.querySelector('button[type="submit"]');
  let prev = null;
  if (btn) { btn.disabled = true; prev = btn.innerHTML; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...'; }

    const res = await fetch('/admin/categories', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token() },
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(()=>({ detail: 'Failed to create category' }));
      throw new Error(err.detail || 'Failed to create category');
    }

    closeModal();
    loadCategories();
    showNotification('Category created successfully!', 'success');
  if (btn) { btn.disabled = false; btn.innerHTML = prev; }
  } catch (e) {
    showNotification(e.message || 'Failed to create category', 'error');
    // keep modal open so user can correct
  }
}

async function updateCategory(e, id) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData();
  formData.append('name', form.name.value);
  formData.append('description', form.description.value || '');
  const iconFile = form.icon?.files && form.icon.files[0];
  if (iconFile) formData.append('icon', iconFile);
  try {
  const btn = form.querySelector('button[type="submit"]');
  let prev = null;
  if (btn) { btn.disabled = true; prev = btn.innerHTML; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...'; }

    const res = await fetch(`/admin/categories/${id}`, {
      method: 'PUT',
      headers: { 'Authorization': 'Bearer ' + token() },
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(()=>({ detail: 'Failed to update category' }));
      throw new Error(err.detail || 'Failed to update category');
    }

    closeModal();
    loadCategories();
    showNotification('Category updated successfully!', 'success');
  if (btn) { btn.disabled = false; btn.innerHTML = prev; }
  } catch (e) {
    showNotification(e.message || 'Failed to update category', 'error');
  }
}

async function deleteCategory(id) {
  if (!confirm('Are you sure you want to delete this category?')) return;
  try {
    const res = await fetch(`/admin/categories/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token() }
    });

    if (!res.ok) {
      const err = await res.json().catch(()=>({ detail: 'Failed to delete category' }));
      throw new Error(err.detail || 'Failed to delete category');
    }

    loadCategories();
    showNotification('Category deleted successfully!', 'success');
  } catch (e) {
    showNotification(e.message || 'Failed to delete category', 'error');
  }
}

// Products
// Load products with server-side pagination (admin endpoint)
let currentSortBy = '';
let currentPageSize = 12;
let currentSearch = '';
let currentCategoryId = '';

async function loadProducts(page = 1, pageSize = null) {
  try {
    const ps = pageSize || currentPageSize;
  const sortParam = currentSortBy ? `&sort_by=${encodeURIComponent(currentSortBy)}` : '';
  const searchParam = currentSearch ? `&search=${encodeURIComponent(currentSearch)}` : '';
  const categoryParam = currentCategoryId ? `&category_id=${encodeURIComponent(currentCategoryId)}` : '';
  const res = await api(`/admin/products?page=${page}&page_size=${ps}${sortParam}${searchParam}${categoryParam}`);
    const grid = document.getElementById('productsList');
    const paginationContainer = document.getElementById('productsPagination');
    grid.innerHTML = '';
    paginationContainer.innerHTML = '';

    res.items.forEach(p => {
      const card = document.createElement('div');
      card.className = 'item-card';
      const img = p.images && p.images[0] ? p.images[0] : 'https://via.placeholder.com/400x300?text=No+Image';
      card.innerHTML = `
        <a href="/admin/product/${p.product_code}/edit" style="text-decoration:none;color:inherit">
          <img src="${img}" alt="${escapeHtml(p.name)}" class="item-image" onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
        </a>
        <div class="item-content">
          <h3 class="item-title">${escapeHtml(p.name)}</h3>
          <div class="item-meta">
            <span><i class="fas fa-barcode"></i> ${p.product_code}</span>
            <span><i class="fas fa-rupee-sign"></i> ${p.normal_price}${p.offer_price ? ` <span class="badge badge-success">Offer: ₹${p.offer_price}</span>` : ''}</span>
            <span><i class="fas fa-tag"></i> ${p.category?.name || 'Uncategorized'}</span>
            ${p.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>'}
          </div>
          <div class="item-actions">
            <a class="btn btn-primary" href="/admin/product/${p.product_code}/edit">
              <i class="fas fa-eye"></i> View
            </a>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });

  // Render pagination
    const meta = res.meta;
    function renderPagination(meta) {
      const frag = document.createDocumentFragment();
      const prev = document.createElement('button');
      prev.className = 'pagination-button';
      prev.textContent = 'Prev';
      prev.disabled = !meta.has_previous;
  prev.addEventListener('click', () => loadProducts(meta.page - 1));
      frag.appendChild(prev);

      // show up to 7 page numbers centered on current
      const total = meta.total_pages;
      const current = meta.page;
      const range = [];
      const delta = 3;
      const left = Math.max(1, current - delta);
      const right = Math.min(total, current + delta);
      for (let i = left; i <= right; i++) range.push(i);

      if (left > 1) {
        const b = document.createElement('button');
        b.className = 'pagination-button';
        b.textContent = '1';
  b.addEventListener('click', () => loadProducts(1));
        frag.appendChild(b);
        if (left > 2) {
          const dots = document.createElement('span');
          dots.textContent = '...';
          dots.style.padding = '8px';
          frag.appendChild(dots);
        }
      }

      range.forEach(pn => {
        const btn = document.createElement('button');
        btn.className = 'pagination-button' + (pn === current ? ' active' : '');
        btn.textContent = pn;
  btn.addEventListener('click', () => loadProducts(pn));
        frag.appendChild(btn);
      });

      if (right < total) {
        if (right < total - 1) {
          const dots = document.createElement('span');
          dots.textContent = '...';
          dots.style.padding = '8px';
          frag.appendChild(dots);
        }
        const b = document.createElement('button');
        b.className = 'pagination-button';
        b.textContent = total;
  b.addEventListener('click', () => loadProducts(total));
        frag.appendChild(b);
      }

      const next = document.createElement('button');
      next.className = 'pagination-button';
      next.textContent = 'Next';
      next.disabled = !meta.has_next;
  next.addEventListener('click', () => loadProducts(meta.page + 1));
      frag.appendChild(next);

      paginationContainer.appendChild(frag);
    }

    renderPagination(meta);
    // setup gallery click handlers for thumbnails in the grid (lightbox)
    document.querySelectorAll('#productsList .item-card img').forEach(img => {
      img.addEventListener('click', (e) => {
        // open in new tab for quick preview on grid click (detail page is primary edit)
        const src = e.currentTarget.getAttribute('src');
        if (src) window.open(src, '_blank');
      });
    });
  } catch (e) {
    console.error(e);
    document.getElementById('productsList').innerHTML = '<div class="muted">Failed to load products</div>';
  }
}

// Called on page load to wire the page-size and sort controls
async function setupProductsControls() {
  const pageSizeSelect = document.getElementById('pageSizeSelect');
  const sortBySelect = document.getElementById('sortBySelect');
  const categorySelect = document.getElementById('categoryFilterSelect');
  if (pageSizeSelect) {
    pageSizeSelect.value = String(currentPageSize);
    pageSizeSelect.addEventListener('change', () => {
      currentPageSize = parseInt(pageSizeSelect.value, 10) || 12;
      loadProducts(1);
    });
  }
  if (sortBySelect) {
    sortBySelect.addEventListener('change', () => {
      currentSortBy = sortBySelect.value || '';
      loadProducts(1);
    });
  }
  if (categorySelect) {
    // populate categories for filter
    categorySelect.innerHTML = '<option value="">All Categories</option>';
    try {
      const cats = await api('/categories');
      cats.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.name;
        categorySelect.appendChild(opt);
      });
      categorySelect.value = currentCategoryId || '';
      categorySelect.addEventListener('change', () => {
        currentCategoryId = categorySelect.value || '';
        loadProducts(1);
      });
    } catch (e) {
      console.error('Failed to load category filter', e);
    }
  }
}

// Enable lightbox preview and drag-to-reorder for an image-preview-container
function enableImageGallery(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Lightbox overlay
  let overlay = document.getElementById('imageLightboxOverlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'imageLightboxOverlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.85);display:none;align-items:center;justify-content:center;z-index:9999;padding:20px;';
    overlay.innerHTML = '<img id="imageLightboxImg" style="max-width:90%;max-height:90%;border-radius:8px;box-shadow:var(--shadow-xl);" />';
    overlay.addEventListener('click', () => { overlay.style.display = 'none'; });
    document.body.appendChild(overlay);
  }

  function showLightbox(src) {
    const img = document.getElementById('imageLightboxImg');
    img.src = src;
    overlay.style.display = 'flex';
  }

  // Drag and drop reordering
  let dragSrc = null;
  container.querySelectorAll('.image-preview').forEach(item => {
    item.setAttribute('draggable', 'true');
    item.addEventListener('dragstart', (e) => { dragSrc = item; item.style.opacity = '0.4'; });
    item.addEventListener('dragend', () => { dragSrc = null; item.style.opacity = '1'; });
    item.addEventListener('dragover', (e) => { e.preventDefault(); });
    item.addEventListener('drop', (e) => {
      e.preventDefault();
      if (dragSrc && dragSrc !== item) {
        container.insertBefore(dragSrc, item.nextSibling);
      }
    });

    // click to open lightbox
    const img = item.querySelector('img');
    if (img) img.addEventListener('click', (e) => { e.stopPropagation(); showLightbox(img.src); });
  });
}

async function showCreateProduct() {
  const categories = await api('/categories');
  const categoryOptions = categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  
  const content = `
    <form id="productForm" onsubmit="submitProduct(event)">
      <div class="form-row">
        <div class="form-group">
          <label><i class="fas fa-box"></i> Product Name *</label>
          <input type="text" name="name" required placeholder="Enter product name">
        </div>
        <div class="form-group">
          <label><i class="fas fa-barcode"></i> Product Code *</label>
          <input type="text" name="product_code" required placeholder="Enter unique code">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label><i class="fas fa-tag"></i> Category *</label>
          <select name="category_id" required>
            <option value="">Select Category</option>
            ${categoryOptions}
          </select>
        </div>
        <div class="form-group">
          <label><i class="fas fa-rupee-sign"></i> Normal Price *</label>
          <input type="number" name="normal_price" required step="0.01" placeholder="0.00">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label><i class="fas fa-percentage"></i> Offer Price</label>
          <input type="number" name="offer_price" step="0.01" placeholder="0.00">
        </div>
        <div class="form-group">
          <label><i class="fas fa-box"></i> Stock Quantity</label>
          <input type="number" name="stock_quantity" value="0" min="0">
        </div>
      </div>
      <div class="form-group">
        <label><i class="fas fa-toggle-on"></i> Status</label>
        <select name="is_active">
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>
      <div class="form-group">
        <label><i class="fas fa-align-left"></i> Description</label>
        <textarea name="details" placeholder="Enter product description"></textarea>
      </div>
      <div class="form-group">
        <label><i class="fas fa-image"></i> Product Images</label>
        <input type="file" name="images" accept="image/*" multiple onchange="previewImages(event, 'imagePreview')">
        <small class="muted">Select multiple images (JPG, PNG, WebP)</small>
        <div id="imagePreview" class="image-preview-container"></div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">
          <i class="fas fa-plus"></i> Create Product
        </button>
      </div>
    </form>
  `;
  showModal('<i class="fas fa-box"></i> Create New Product', content);
}

async function editProduct(code) {
  try {
    const product = await api(`/products/${code}`);
    const categories = await api('/categories');
    const categoryOptions = categories.map(c => 
      `<option value="${c.id}" ${product.category_id === c.id ? 'selected' : ''}>${c.name}</option>`
    ).join('');
    
    const existingImages = product.images || [];
    const imagePreviewHtml = existingImages.map((url, idx) => `
      <div class="image-preview" data-existing-url="${url}">
        <img src="${url}" alt="Image ${idx + 1}">
        <button type="button" class="image-preview-remove" onclick="removeExistingImage(this)">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `).join('');
    
    const content = `
      <form id="productForm" onsubmit="updateProduct(event, '${code}')">
        <div class="form-row">
          <div class="form-group">
            <label><i class="fas fa-box"></i> Product Name *</label>
            <input type="text" name="name" value="${escapeHtml(product.name)}" required>
          </div>
          <div class="form-group">
            <label><i class="fas fa-barcode"></i> Product Code</label>
            <input type="text" value="${product.product_code}" disabled>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><i class="fas fa-tag"></i> Category *</label>
            <select name="category_id" required>
              <option value="">Select Category</option>
              ${categoryOptions}
            </select>
          </div>
          <div class="form-group">
            <label><i class="fas fa-rupee-sign"></i> Normal Price *</label>
            <input type="number" name="normal_price" value="${product.normal_price}" required step="0.01">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><i class="fas fa-percentage"></i> Offer Price</label>
            <input type="number" name="offer_price" value="${product.offer_price || ''}" step="0.01">
          </div>
          <div class="form-group">
            <label><i class="fas fa-box"></i> Stock Quantity</label>
            <input type="number" name="stock_quantity" value="${product.stock_quantity || 0}" min="0">
          </div>
        </div>
        <div class="form-group">
          <label><i class="fas fa-toggle-on"></i> Status</label>
          <select name="is_active">
            <option value="true" ${product.is_active ? 'selected' : ''}>Active</option>
            <option value="false" ${!product.is_active ? 'selected' : ''}>Inactive</option>
          </select>
        </div>
        <div class="form-group">
          <label><i class="fas fa-align-left"></i> Description</label>
          <textarea name="details">${escapeHtml(product.details || '')}</textarea>
        </div>
        <div class="form-group">
          <label><i class="fas fa-image"></i> Current Images</label>
          <div id="existingImagesContainer" class="image-preview-container">
            ${imagePreviewHtml}
          </div>
        </div>
        <div class="form-group">
          <label><i class="fas fa-plus-circle"></i> Add New Images</label>
          <input type="file" name="images" accept="image/*" multiple onchange="previewImages(event, 'newImagePreview')">
          <small class="muted">Select additional images to add</small>
          <div id="newImagePreview" class="image-preview-container"></div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i> Update Product
          </button>
        </div>
      </form>
    `;
    showModal('<i class="fas fa-edit"></i> Edit Product', content);
  } catch (e) {
    showNotification('Failed to load product', 'error');
  }
}

async function submitProduct(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData();
  
  // Add text fields
  formData.append('product_code', form.product_code.value);
  formData.append('name', form.name.value);
  formData.append('category_id', form.category_id.value);
  formData.append('normal_price', form.normal_price.value);
  formData.append('stock_quantity', form.stock_quantity.value || '0');
  formData.append('is_active', form.is_active.value);
  
  if (form.offer_price.value) {
    formData.append('offer_price', form.offer_price.value);
  }
  if (form.details.value) {
    formData.append('details', form.details.value);
  }
  
  // Add image files
  const imageFiles = form.images.files;
  if (imageFiles.length > 0) {
    for (const file of imageFiles) {
      formData.append('images', file);
    }
  }
  
  try {
    const res = await fetch('/admin/products', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token() },
      body: formData
    });
    
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to create product');
    }
    
    closeModal();
    loadProducts();
    showNotification('Product created successfully!', 'success');
  } catch (e) {
    showNotification(e.message, 'error');
  }
}

async function updateProduct(e, code) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData();
  
  // Add text fields
  formData.append('name', form.name.value);
  formData.append('category_id', form.category_id.value);
  formData.append('normal_price', form.normal_price.value);
  formData.append('stock_quantity', form.stock_quantity.value || '0');
  formData.append('is_active', form.is_active.value);
  
  if (form.offer_price.value) {
    formData.append('offer_price', form.offer_price.value);
  }
  if (form.details.value) {
    formData.append('details', form.details.value);
  }
  
  // Collect remaining existing images
  const existingImages = [];
  document.querySelectorAll('#existingImagesContainer .image-preview').forEach(preview => {
    const url = preview.getAttribute('data-existing-url');
    if (url) existingImages.push(url);
  });
  
  // Add new image files
  const imageFiles = form.images.files;
  const hasNewImages = imageFiles.length > 0;
  
  if (hasNewImages) {
    for (const file of imageFiles) {
      formData.append('images', file);
    }
    formData.append('replace_images', 'false'); // Append new images
  }
  
  // If we have existing images and no new images, or we need to preserve existing
  if (existingImages.length > 0) {
    formData.append('image_urls', JSON.stringify(existingImages));
    if (!hasNewImages) {
      formData.append('replace_images', 'true'); // Keep only existing
    }
  }
  
  try {
    const res = await fetch(`/admin/products/${code}`, {
      method: 'PUT',
      headers: { 'Authorization': 'Bearer ' + token() },
      body: formData
    });
    
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to update product');
    }
    
    closeModal();
    loadProducts();
    showNotification('Product updated successfully!', 'success');
  } catch (e) {
    showNotification(e.message, 'error');
  }
}

async function deleteProduct(code) {
  if (!confirm('Are you sure you want to delete this product?')) return;
  try {
    await fetch(`/admin/products/${code}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token() }
    });
    loadProducts();
    showNotification('Product deleted successfully!', 'success');
  } catch (e) {
    showNotification('Failed to delete product', 'error');
  }
}

// Banners
async function loadBanners() {
  try {
    const banners = await api('/admin/banners');
    const grid = document.getElementById('bannersList');
    grid.innerHTML = '';
    banners.forEach(b => {
      const card = document.createElement('div');
      card.className = 'item-card';
      card.innerHTML = `
        <img src="${b.image_url}" alt="${escapeHtml(b.title || 'Banner')}" class="item-image">
        <div class="item-content">
          <h3 class="item-title">${escapeHtml(b.title || 'Banner')}</h3>
          <div class="item-meta">
            <span><i class="fas fa-sort"></i> Display Order: ${b.display_order}</span>
            ${b.link_url ? `<span><i class="fas fa-link"></i> <a href="${b.link_url}" target="_blank" style="color: var(--primary)">Link</a></span>` : ''}
            ${b.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>'}
          </div>
          <div class="item-actions">
            <button class="btn btn-primary" onclick="editBanner(${b.id})">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn btn-danger" onclick="deleteBanner(${b.id})">
              <i class="fas fa-trash"></i> Delete
            </button>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    console.error(e);
  }
}

function showCreateBanner() {
  const content = `
    <form id="bannerForm" onsubmit="submitBanners(event)">
      <div class="form-group">
        <label><i class="fas fa-images"></i> Upload Banner Images *</label>
        <input type="file" id="bannerImages" name="images" accept="image/*" multiple required onchange="previewImages(event, 'bannerPreview')">
        <small class="muted">Select one or multiple banner images (JPG, PNG, WebP)</small>
        <div id="bannerPreview" class="image-preview-container"></div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">
          <i class="fas fa-upload"></i> Upload Banners
        </button>
      </div>
    </form>
  `;
  showModal('<i class="fas fa-images"></i> Upload Banners', content);
}

async function submitBanners(e) {
  e.preventDefault();
  const form = e.target;
  const files = form.images.files;
  if (!files.length) {
    showNotification('Please select at least one image', 'error');
    return;
  }
  
  const formData = new FormData();
  for (const file of files) {
    formData.append('images', file);
  }
  
  try {
    const res = await fetch('/admin/banners/upload-multiple', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token() },
      body: formData
    });
    
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to upload banners');
    }
    
    closeModal();
    loadBanners();
    showNotification('Banners uploaded successfully!', 'success');
  } catch (e) {
    showNotification(e.message, 'error');
  }
}

async function editBanner(id) {
  try {
    const banner = await api(`/admin/banners/${id}`);
    
    const content = `
      <form id="bannerForm" onsubmit="updateBanner(event, ${id})">
        <div class="form-group">
          <label><i class="fas fa-heading"></i> Title</label>
          <input type="text" name="title" value="${escapeHtml(banner.title || '')}">
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><i class="fas fa-sort"></i> Display Order</label>
            <input type="number" name="display_order" value="${banner.display_order}">
          </div>
          <div class="form-group">
            <label><i class="fas fa-toggle-on"></i> Status</label>
            <select name="is_active">
              <option value="true" ${banner.is_active ? 'selected' : ''}>Active</option>
              <option value="false" ${!banner.is_active ? 'selected' : ''}>Inactive</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label><i class="fas fa-link"></i> Link URL (Optional)</label>
          <input type="url" name="link_url" value="${escapeHtml(banner.link_url || '')}" placeholder="https://example.com">
        </div>
        <div class="form-group">
          <label>Current Image</label>
          <img src="${banner.image_url}" style="max-width: 100%; height: auto; border-radius: var(--radius-md); display: block;">
        </div>
        <div class="form-actions">
          <button type="button" class="btn" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i> Update Banner
          </button>
        </div>
      </form>
    `;
    showModal('<i class="fas fa-edit"></i> Edit Banner', content);
  } catch (e) {
    showNotification('Failed to load banner', 'error');
  }
}

async function updateBanner(e, id) {
  e.preventDefault();
  const form = e.target;
  const data = {
    title: form.title.value,
    display_order: parseInt(form.display_order.value),
    is_active: form.is_active.value === 'true'
  };
  
  if (form.link_url.value) {
    data.link_url = form.link_url.value;
  }
  
  try {
    const res = await fetch(`/admin/banners/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token() },
      body: JSON.stringify(data)
    });
    
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to update banner');
    }
    
    closeModal();
    loadBanners();
    showNotification('Banner updated successfully!', 'success');
  } catch (e) {
    showNotification(e.message, 'error');
  }
}

async function deleteBanner(id) {
  if (!confirm('Are you sure you want to delete this banner?')) return;
  try {
    const res = await fetch(`/admin/banners/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token() }
    });
    
    if (!res.ok && res.status !== 204) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to delete banner');
    }
    
    loadBanners();
    showNotification('Banner deleted successfully!', 'success');
  } catch (e) {
    showNotification(e.message || 'Failed to delete banner', 'error');
  }
}

// Combos
async function loadCombos() {
  try {
    const res = await api('/combos?page=1&page_size=50');
    const grid = document.getElementById('combosList');
    grid.innerHTML = '';
    res.items.forEach(c => {
      const card = document.createElement('div');
      card.className = 'item-card';
      const priceDisplay = (c.combo_price !== undefined && c.combo_price !== null) ? `₹${c.combo_price}` : '—';
      card.innerHTML = `
        <div class="item-content">
          <h3 class="item-title"><i class="fas fa-layer-group"></i> ${escapeHtml(c.name || '')}</h3>
          <div class="item-meta">
            <span><i class="fas fa-barcode"></i> ${escapeHtml(c.combo_code || '')}</span>
            <span><i class="fas fa-rupee-sign"></i> ${priceDisplay}</span>
            ${c.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>'}
          </div>
          <div class="item-actions">
            <button class="btn btn-primary" onclick="editCombo('${escapeHtml(c.combo_code || '')}')">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn btn-danger" onclick="deleteCombo('${escapeHtml(c.combo_code || '')}')">
              <i class="fas fa-trash"></i> Delete
            </button>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    console.error(e);
  }
}

function showCreateCombo() {
  const content = `
    <form id="comboForm" onsubmit="submitCombo(event)">
      <div class="form-row">
        <div class="form-group">
          <label><i class="fas fa-layer-group"></i> Combo Name *</label>
          <input type="text" name="name" required>
        </div>
        <div class="form-group">
          <label><i class="fas fa-barcode"></i> Combo Code *</label>
          <input type="text" name="combo_code" required>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label><i class="fas fa-rupee-sign"></i> Price *</label>
          <input type="number" name="combo_price" required step="0.01">
        </div>
        <div class="form-group">
          <label><i class="fas fa-toggle-on"></i> Status</label>
          <select name="is_active">
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label><i class="fas fa-align-left"></i> Description</label>
        <textarea name="description"></textarea>
      </div>

      <div class="form-group">
        <label><i class="fas fa-search"></i> Add Products</label>
        <input type="text" id="comboProductSearch" placeholder="Search products by name or code..." autocomplete="off">
        <div id="comboProductResults" class="items-grid" style="margin-top:8px"></div>
        <div id="comboSelectedProducts" style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px"></div>
        <input type="hidden" name="product_ids" id="comboProductIdsHidden" value="">
        <small class="muted">Search and pick products to include in the combo. Selected products will be submitted automatically.</small>
      </div>

      <div class="form-actions">
        <button type="button" class="btn" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">
          <i class="fas fa-plus"></i> Create Combo
        </button>
      </div>
    </form>
  `;
  showModal('<i class="fas fa-gift"></i> Create New Combo', content);

  // Initialize the combo product selector for the create form (use rAF to ensure DOM is ready)
  requestAnimationFrame(() => { try { setupComboSelector('combo', ''); } catch (e) { console.error('setupComboSelector(combo) failed', e); } });
}

async function submitCombo(e) {
  e.preventDefault();
  const form = e.target;
    const productIds = form.product_ids.value ? form.product_ids.value.split(',').map(s => parseInt(s.trim())).filter(Boolean) : [];
    const productsPayload = productIds.map(id => ({ product_id: id, quantity: 1 }));
    const data = {
      name: form.name.value,
      combo_code: form.combo_code.value,
      combo_price: parseFloat(form.combo_price.value),
      description: form.description.value,
      is_active: form.is_active.value === 'true',
      products: productsPayload
    };
    try {
      const res = await fetch('/admin/combos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token() },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        const err = await res.json().catch(()=>({ detail: 'Failed to create combo' }));
        throw new Error(err.detail || 'Failed to create combo');
      }
    closeModal();
    loadCombos();
    showNotification('Combo created successfully!', 'success');
  } catch (e) {
    showNotification('Failed to create combo', 'error');
  }
}

async function editCombo(code) {
  try {
    let combo = null;

    // Prefer fetching a single combo if the API exposes it
    try {
      combo = await api(`/combos/${encodeURIComponent(code)}`);
    } catch (err) {
      // Fallback to paginated list search if single-get isn't available or fails
      try {
        const res = await api('/combos?page=1&page_size=200');
        if (res && Array.isArray(res.items)) combo = res.items.find(x => x.combo_code === code) || null;
      } catch (err2) {
        combo = null;
      }
    }

    // If combo still not present, provide an empty object so modal renders
    if (!combo) {
      combo = {
        name: null,
        combo_code: code,
        combo_price: null,
        is_active: false,
        description: null,
        products: []
      };
    }

    // Normalize product IDs: backend may return either {product_id,...} or {product: {...}, quantity}
    const productIds = (combo.products || []).map(p => {
      if (p.product_id) return String(p.product_id);
      if (p.product && (p.product.id || p.product.product_id)) return String(p.product.id || p.product.product_id);
      if (p.product && p.product.product_code) return String(p.product.product_code);
      // If the product field is a number (rare), return it
      if (typeof p === 'number') return String(p);
      return null;
    }).filter(Boolean).join(', ');

    const comboPriceVal = combo.combo_price !== undefined && combo.combo_price !== null ? combo.combo_price : (combo.price !== undefined ? combo.price : '');
  const content = `
      <form id="comboForm" onsubmit="updateCombo(event, '${escapeHtml(code)}')">
        <div class="form-row">
          <div class="form-group">
            <label><i class="fas fa-layer-group"></i> Combo Name *</label>
            <input type="text" name="name" required value="${escapeHtml(combo.name || '')}">
          </div>
          <div class="form-group">
            <label><i class="fas fa-barcode"></i> Combo Code</label>
            <input type="text" name="combo_code" value="${escapeHtml(combo.combo_code || '')}" disabled>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label><i class="fas fa-rupee-sign"></i> Price *</label>
            <input type="number" name="combo_price" required step="0.01" value="${escapeHtml(String(comboPriceVal))}">
          </div>
          <div class="form-group">
            <label><i class="fas fa-toggle-on"></i> Status</label>
            <select name="is_active">
              <option value="true" ${combo.is_active ? 'selected' : ''}>Active</option>
              <option value="false" ${!combo.is_active ? 'selected' : ''}>Inactive</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label><i class="fas fa-align-left"></i> Description</label>
          <textarea name="description">${escapeHtml(combo.description || '')}</textarea>
        </div>
        <div class="form-group">
          <label><i class="fas fa-search"></i> Add Products</label>
          <input type="text" id="comboEditProductSearch" placeholder="Search products by name or code..." autocomplete="off">
          <div id="comboEditProductResults" class="items-grid" style="margin-top:8px"></div>
          <div id="comboEditSelectedProducts" style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px"></div>
          <input type="hidden" name="product_ids" id="comboEditProductIdsHidden" value="${escapeHtml(productIds)}">
          <small class="muted">Search and pick products to include in the combo. Selected products will be submitted automatically.</small>
        </div>
        <div class="form-actions">
          <button type="button" class="btn" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i> Update Combo
          </button>
        </div>
      </form>
    `;

  showModal('<i class="fas fa-edit"></i> Edit Combo', content);
  // Initialize selector with existing IDs (productIds contains comma separated string)
  requestAnimationFrame(() => { try { setupComboSelector('comboEdit', productIds); } catch (e) { console.error('setupComboSelector(comboEdit) failed', e); } });
  } catch (e) {
    showNotification(e.message || 'Failed to load combo', 'error');
  }
}

async function updateCombo(e, code) {
  e.preventDefault();
  const form = e.target;
  const productIds = form.product_ids.value ? form.product_ids.value.split(',').map(s => parseInt(s.trim())).filter(Boolean) : [];
  const productsPayload = productIds.map(id => ({ product_id: id, quantity: 1 }));
  const data = {
    name: form.name.value,
    combo_price: parseFloat(form.combo_price.value),
    description: form.description.value,
    is_active: form.is_active.value === 'true',
    products: productsPayload
  };
  try {
    const res = await fetch(`/admin/combos/${code}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token() },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({ detail: 'Failed to update combo' }));
      throw new Error(err.detail || 'Failed to update combo');
    }
    closeModal();
    loadCombos();
    showNotification('Combo updated successfully!', 'success');
  } catch (e) {
    showNotification(e.message || 'Failed to update combo', 'error');
  }
}

async function deleteCombo(code) {
  if (!confirm('Are you sure you want to delete this combo?')) return;
  try {
    await fetch(`/admin/combos/${code}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token() }
    });
    loadCombos();
    showNotification('Combo deleted successfully!', 'success');
  } catch (e) {
    showNotification('Failed to delete combo', 'error');
  }
}

// New Arrivals
async function loadNewArrivals() {
  try {
    const res = await api('/new-arrivals?page=1&page_size=50');
    const grid = document.getElementById('newArrivalsList');
    grid.innerHTML = '';
    res.items.forEach(n => {
      const p = n.product || {};
      const card = document.createElement('div');
      card.className = 'item-card';
      const img = p.images && p.images[0] ? p.images[0] : 'https://via.placeholder.com/400x300?text=No+Image';
      card.innerHTML = `
        <img src="${img}" alt="${escapeHtml(p.name || 'Product')}" class="item-image" onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
        <div class="item-content">
          <h3 class="item-title">${escapeHtml(p.name || 'Product')}</h3>
          <div class="item-meta">
            <span><i class="fas fa-hashtag"></i> Product ID: ${p.id}</span>
            <span><i class="fas fa-barcode"></i> ${p.product_code || 'N/A'}</span>
          </div>
          <div class="item-actions">
            <button class="btn btn-danger" onclick="removeNewArrival(${p.id})">
              <i class="fas fa-times"></i> Remove
            </button>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    console.error(e);
  }
}

function showAddNewArrival() {
  const content = `
    <form id="newArrivalForm" onsubmit="submitNewArrival(event)">
      <div class="form-group">
        <label><i class="fas fa-search"></i> Select Product</label>
        <input type="text" id="newArrivalProductSearch" placeholder="Search products by name or code..." autocomplete="off">
        <div id="newArrivalProductResults" class="items-grid" style="margin-top:8px"></div>
        <div id="newArrivalSelectedProducts" style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px"></div>
        <input type="hidden" name="product_id" id="newArrivalProductIdsHidden" value="">
        <small class="muted">Search and pick one product to add to new arrivals.</small>
      </div>
      <div class="form-actions">
        <button type="button" class="btn" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">
          <i class="fas fa-plus"></i> Add to New Arrivals
        </button>
      </div>
    </form>
  `;
  showModal('<i class="fas fa-star"></i> Add to New Arrivals', content);

  // initialize single-select combo-like selector for new arrivals
  requestAnimationFrame(() => {
    try { setupComboSelector('newArrival', ''); } catch (e) { console.error('setupComboSelector(newArrival) failed', e); }
    // override add to ensure single selection
    window.addComboProduct_newArrival = function(product) {
      if (!product || !product.id) return;
      window.newArrivalSelectedList = [product];
      const S = document.getElementById('newArrivalSelectedProducts');
      if (S) {
        S.innerHTML = `<div class="selected-pill" data-id="${product.id}" style="display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:var(--surface);">
            <div style="font-weight:600">${escapeHtml(product.name || product.product_code || ('#'+product.id))}</div>
            <button type="button" class="btn" onclick="window.removeComboProduct_newArrival(${product.id})" style="padding:6px 8px;min-width:24px">&times;</button>
          </div>`;
      }
      const H = document.getElementById('newArrivalProductIdsHidden'); if (H) H.value = String(product.id);
    };
    window.removeComboProduct_newArrival = function(id) {
      window.newArrivalSelectedList = [];
      const S = document.getElementById('newArrivalSelectedProducts'); if (S) S.innerHTML = '';
      const H = document.getElementById('newArrivalProductIdsHidden'); if (H) H.value = '';
    };
  });
}

async function submitNewArrival(e) {
  e.preventDefault();
  const form = e.target;
  // read hidden selected product id (first one)
  const hidden = document.getElementById('newArrivalProductIdsHidden');
  const pid = hidden && hidden.value ? parseInt(hidden.value) : null;
  if (!pid) { showNotification('Please select a product', 'error'); return; }
  const data = { product_id: pid };
  try {
    await fetch('/admin/new-arrivals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token() },
      body: JSON.stringify(data)
    });
    closeModal();
    loadNewArrivals();
    showNotification('Product added to new arrivals!', 'success');
  } catch (e) {
    showNotification('Failed to add to new arrivals', 'error');
  }
}

async function removeNewArrival(productId) {
  if (!confirm('Remove this product from new arrivals?')) return;
  try {
    await fetch(`/admin/new-arrivals/${productId}`, {
      method: 'DELETE',
      headers: { 'Authorization': 'Bearer ' + token() }
    });
    loadNewArrivals();
    showNotification('Removed from new arrivals!', 'success');
  } catch (e) {
    showNotification('Failed to remove', 'error');
  }
}

// Utility Functions
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function previewImages(event, containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  const files = event.target.files;
  
  if (files.length === 0) return;
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const preview = document.createElement('div');
      preview.className = 'image-preview';
      preview.innerHTML = `
        <img src="${e.target.result}" alt="${file.name}">
        <button type="button" class="image-preview-remove" onclick="removeImagePreview(this, '${containerId}')">
          <i class="fas fa-times"></i>
        </button>
      `;
      container.appendChild(preview);
    };
    
    reader.readAsDataURL(file);
  }
}

/* Combo product selector helper
   prefix: string prefix used for element ids (e.g. 'combo' or 'comboEdit')
   initial: either empty string or comma-separated product ids (as used by server)
*/
function setupComboSelector(prefix, initial) {
  const searchInput = document.getElementById(prefix + 'ProductSearch');
  const resultsEl = document.getElementById(prefix + 'ProductResults');
  const selectedEl = document.getElementById(prefix + 'SelectedProducts');
  const hiddenEl = document.getElementById(prefix + 'ProductIdsHidden') || document.getElementById(prefix + 'ProductIdsHidden'.replace('ProductIdsHidden','ProductIdsHidden'));
  const hiddenIds = document.getElementById(prefix + 'ProductIdsHidden') || document.getElementById(prefix + 'ProductIdsHidden');
  const hiddenInput = document.getElementById(prefix + 'ProductIdsHidden') || document.getElementById(prefix + 'ProductIdsHidden');

  // Fallbacks for edit prefix naming
  const resultsElAlt = resultsEl || document.getElementById(prefix + 'ProductResults');
  const selectedElAlt = selectedEl || document.getElementById(prefix + 'SelectedProducts');
  const hiddenElAlt = document.getElementById(prefix + 'ProductIdsHidden') || document.getElementById(prefix + 'ProductIdsHidden') || document.getElementById(prefix + 'ProductIdsHidden');

  const R = resultsElAlt;
  const S = selectedElAlt;
  const H = document.getElementById(prefix + 'ProductIdsHidden') || document.getElementById(prefix + 'ProductIdsHidden') || document.getElementById(prefix + 'ProductIdsHidden');

  // Selected list in-memory
  window[prefix + 'SelectedList'] = [];

  function updateHidden() {
    const ids = window[prefix + 'SelectedList'].map(p => p.id);
    if (H) H.value = ids.join(', ');
  }

  function renderSelected() {
    if (!S) return;
    S.innerHTML = window[prefix + 'SelectedList'].map(p => `
      <div class="selected-pill" data-id="${p.id}" style="display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:var(--surface);">
        <div style="font-weight:600">${escapeHtml(p.name || p.product_code || ('#'+p.id))}</div>
        <button type="button" class="btn" onclick="window.removeComboProduct_${prefix}(${p.id})" style="padding:6px 8px;min-width:24px">&times;</button>
      </div>
    `).join('');
  }

  // Public remove function (namespaced)
  window['removeComboProduct_' + prefix] = function(id) {
    window[prefix + 'SelectedList'] = window[prefix + 'SelectedList'].filter(x => x.id !== id);
    renderSelected();
    updateHidden();
  };

  window['addComboProduct_' + prefix] = function(product) {
    if (!product || !product.id) return;
    if (window[prefix + 'SelectedList'].some(x => x.id === product.id)) return;
    window[prefix + 'SelectedList'].push(product);
    renderSelected();
    updateHidden();
  };

  // search
  let debounceTimer = null;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(async () => {
        if (!q || q.length < 2) { if (R) R.innerHTML = ''; return; }
        try {
          const res = await api(`/admin/products?page=1&page_size=8&search=${encodeURIComponent(q)}`);
          const items = res.items || [];
          if (R) {
            R.innerHTML = items.map(p => `
              <div class="item-card" style="display:flex;align-items:center;gap:8px;">
                <img src="${p.images && p.images[0] ? p.images[0] : 'https://via.placeholder.com/80x60?text=No+Image'}" style="width:72px;height:56px;object-fit:cover;border-radius:6px"/>
                <div style="flex:1">
                  <div style="font-weight:600">${escapeHtml(p.name)}</div>
                  <div class="muted small">${escapeHtml(p.product_code || '')} • ₹${p.normal_price || ''}</div>
                </div>
                <div>
                  <button type="button" class="btn btn-primary add-combo-btn" data-id="${p.id}" data-name="${escapeHtml(p.name)}" data-code="${escapeHtml(p.product_code || '')}" data-price="${p.normal_price || ''}">Add</button>
                </div>
              </div>
            `).join('');

            // attach handlers
            R.querySelectorAll('.add-combo-btn').forEach(btn => {
              btn.addEventListener('click', (ev) => {
                const b = ev.currentTarget;
                const product = {
                  id: parseInt(b.getAttribute('data-id')),
                  name: b.getAttribute('data-name'),
                  product_code: b.getAttribute('data-code'),
                  normal_price: parseFloat(b.getAttribute('data-price')) || 0
                };
                window['addComboProduct_' + prefix](product);
              });
            });
          }
        } catch (err) {
          if (R) R.innerHTML = '<div class="muted">Failed to search</div>';
        }
      }, 260);
    });
  }

  // Initialize with initial ids (comma separated) if provided
  if (initial) {
    const ids = (typeof initial === 'string' ? initial.split(',').map(s => s.trim()).filter(Boolean) : (Array.isArray(initial) ? initial : []) ).map(x => x);
    ids.forEach(id => {
      const parsed = parseInt(id);
      if (!isNaN(parsed)) {
        // create placeholder entry (we'll try to fetch details lazily)
        const p = { id: parsed, name: `#${parsed}`, product_code: '' };
        window[prefix + 'SelectedList'].push(p);
      }
    });
    renderSelected();
    updateHidden();
  }
}

function removeImagePreview(button, containerId) {
  button.parentElement.remove();
  // Clear the file input if no previews remain
  const container = document.getElementById(containerId);
  if (container.children.length === 0) {
    const form = button.closest('form');
    // Try to find the file input that produced this preview. First try matching onchange, then fallback to name='icon'.
    let fileInput = null;
    try {
      fileInput = form.querySelector(`input[type="file"][onchange*="${containerId}"]`);
    } catch (e) {
      fileInput = null;
    }
    if (!fileInput) fileInput = form.querySelector('input[type="file"][name="icon"]') || form.querySelector('input[type="file"]');
    if (fileInput) fileInput.value = '';
  }
}

function removeExistingImage(button) {
  if (confirm('Remove this image?')) {
    const parent = button.parentElement;
    // if inside a form for category edit, mark remove_icon so server clears the icon
    const form = button.closest('form');
    if (form) {
      const hidden = form.querySelector('input[name="remove_icon"]');
      if (hidden) hidden.value = 'true';
    }
    parent.remove();
  }
}

function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 90px;
    right: 20px;
    padding: 16px 24px;
    background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
    color: white;
    border-radius: 12px;
    box-shadow: var(--shadow-lg);
    z-index: 300;
    animation: slideIn 0.3s ease;
    font-weight: 500;
  `;
  notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> ${message}`;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Product Search (server-side) with debounce
function debounce(fn, wait) {
  let t = null;
  return function(...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), wait);
  };
}

const productSearchInput = document.getElementById('productSearch');
if (productSearchInput) {
  productSearchInput.addEventListener('input', debounce((e) => {
    currentSearch = e.target.value.trim();
    loadProducts(1);
  }, 400));
}

// Initialize on load
window.addEventListener('load', async () => {
  if (!token()) {
    if (location.pathname !== '/admin/login') location.href = '/admin/login';
    return;
  }

  // Load initial data; ensure controls are set up before loading products
  loadStats();
  loadCategories();
  await setupProductsControls();
  await loadProducts();
  loadBanners();
  loadCombos();
  loadNewArrivals();

  // Add CSS animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
});

 


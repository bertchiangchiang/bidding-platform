let currentTender = null;

function openQuoteForm(tender) {
  currentTender = tender;
  document.getElementById('quote-form').style.display = '';
  document.getElementById('qf-tender').textContent = '(' + tender + ')';
  document.getElementById('quote-form').scrollIntoView({behavior: 'smooth'});
}

function addRow() {
  const tbody = document.querySelector('#qf-items tbody');
  tbody.insertAdjacentHTML('beforeend', `
    <tr>
      <td><input class="form-control i-name"></td>
      <td><input class="form-control i-qty" type="number" value="1"></td>
      <td><input class="form-control i-price" type="number" step="0.01"></td>
      <td><input class="form-control i-remark"></td>
    </tr>`);
}

async function submitQuote() {
  const items = [];
  document.querySelectorAll('#qf-items tbody tr').forEach(tr => {
    const name = tr.querySelector('.i-name').value.trim();
    if (!name) return;
    items.push({
      item_name: name,
      qty: parseFloat(tr.querySelector('.i-qty').value || 0),
      unit_price: parseFloat(tr.querySelector('.i-price').value || 0),
      remark: tr.querySelector('.i-remark').value.trim()
    });
  });
  const payload = {
    tender: currentTender,
    supplier_name: document.getElementById('qf-supplier').value.trim(),
    items: JSON.stringify(items)
  };
  const resp = await fetch('/api/method/bidding.api.submit_quote', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token
    },
    body: JSON.stringify(payload)
  });
  const data = await resp.json();
  if (resp.ok) {
    document.getElementById('qf-msg').className = 'mt-2 text-success';
    document.getElementById('qf-msg').textContent =
      '报价成功，单号：' + (data.message && data.message.name || '');
    loadRanking(currentTender);
  } else {
    document.getElementById('qf-msg').textContent =
      (data.exception || data._server_messages || '提交失败');
  }
}

async function loadRanking(tender) {
  const resp = await fetch('/api/method/bidding.api.get_ranking?tender=' + encodeURIComponent(tender));
  const data = await resp.json();
  const rows = (data.message && data.message.ranking) || [];
  const isAdmin = data.message && data.message.is_admin;
  let html = '<table class="table table-sm"><thead><tr><th>名次</th><th>供应商</th>';
  html += isAdmin ? '<th>报价总额</th>' : '<th>报价总额</th>';
  html += '</tr></thead><tbody>';
  if (!rows.length) html += '<tr><td colspan="3" class="text-muted">暂无有效报价</td></tr>';
  rows.forEach(r => {
    const price = (isAdmin || r.is_me) ? ('¥ ' + (r.total_price || 0)) : '<span class="text-muted">保密</span>';
    html += `<tr><td>${r.rank}</td><td>${r.supplier_name}${r.is_me ? ' <span class="badge bg-primary">我的报价</span>' : ''}</td><td>${price}</td></tr>`;
  });
  html += '</tbody></table>';
  document.getElementById('ranking-body').innerHTML = html;
  document.getElementById('ranking').style.display = '';
  document.getElementById('ranking').scrollIntoView({behavior: 'smooth'});
}

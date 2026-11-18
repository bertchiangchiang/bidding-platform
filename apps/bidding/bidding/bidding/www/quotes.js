let currentTender = null;
let currentRanking = null;

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

async function apiPost(method, payload) {
  const resp = await fetch('/api/method/' + method, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token
    },
    body: JSON.stringify(payload)
  });
  const data = await resp.json();
  return {ok: resp.ok, data: data};
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
  const {ok, data} = await apiPost('bidding.api.submit_quote', payload);
  if (ok) {
    document.getElementById('qf-msg').className = 'mt-2 text-success';
    document.getElementById('qf-msg').textContent =
      '报价成功，单号：' + (data.message && data.message.name || '');
    loadRanking(currentTender);
  } else {
    document.getElementById('qf-msg').textContent =
      (data.exception || data._server_messages || '提交失败');
  }
}

async function awardQuote(quote) {
  if (!confirm('确认定标给该供应商？定标后全流程锁定。')) return;
  const {ok, data} = await apiPost('bidding.api.award', {quote: quote});
  if (ok) {
    loadRanking(currentTender);
  } else {
    alert(data.exception || data._server_messages || '定标失败');
  }
}

async function loadRanking(tender, mode) {
  let url = '/api/method/bidding.api.get_ranking?tender=' + encodeURIComponent(tender);
  if (mode) url += '&mode=' + encodeURIComponent(mode);
  const resp = await fetch(url);
  const data = await resp.json();
  const msg = data.message || {};
  const rows = msg.ranking || [];
  const isAdmin = msg.is_admin;
  const scoreMode = msg.mode === 'score';
  currentRanking = {tender: tender, mode: msg.mode, status: msg.tender_status};
  let html = '<table class="table table-sm"><thead><tr><th>名次</th><th>供应商</th>';
  html += scoreMode ? '<th>加权总分</th>' : '<th>报价总额</th>';
  html += '<th>报价总额</th></tr></thead><tbody>';
  if (!rows.length) html += '<tr><td colspan="4" class="text-muted">暂无有效报价</td></tr>';
  rows.forEach(r => {
    const main = scoreMode
      ? (r.total_score != null ? r.total_score + ' 分' : '<span class="text-muted">未评分</span>')
      : '¥ ' + (r.total_price || 0);
    const price = (isAdmin || r.is_me) ? ('¥ ' + (r.total_price || 0)) : '<span class="text-muted">保密</span>';
    const badge = (r.awarded ? ' <span class="badge bg-success">中标</span>' : '')
      + (r.is_me ? ' <span class="badge bg-primary">我的报价</span>' : '');
    let awardBtn = '';
    if (isAdmin && !r.awarded && msg.tender_status === '已截止') {
      awardBtn = ` <button class="btn btn-outline-primary btn-sm py-0 px-1" onclick="awardQuote('${r.quote}')">定标</button>`;
    }
    html += `<tr><td>${r.rank}</td><td>${r.supplier_name}${badge}${awardBtn}</td><td>${main}</td><td>${price}</td></tr>`;
  });
  html += '</tbody></table>';
  if (scoreMode && isAdmin) {
    html += '<button class="btn btn-link btn-sm" onclick="loadRanking(currentTender, \'price\')">按总价查看</button>';
  } else if (isAdmin && msg.has_score_template) {
    html += '<button class="btn btn-link btn-sm" onclick="loadRanking(currentTender, \'score\')">按评分查看</button>';
  }
  document.getElementById('ranking-body').innerHTML = html;
  document.getElementById('ranking').style.display = '';
  document.getElementById('ranking').scrollIntoView({behavior: 'smooth'});
}

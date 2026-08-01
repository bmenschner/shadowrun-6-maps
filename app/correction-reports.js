(() => {
  const asString = value => String(value == null ? '' : value).trim();

  function normalizeCoordinate(value) {
    if (!value) return null;
    if (typeof value === 'string') {
      const parts = value.trim().split(/[;,\s]+/).filter(Boolean);
      if (parts.length !== 2) return null;
      value = { lat: parts[0], lng: parts[1] };
    }
    const lat = Number(value.lat);
    const lng = Number(value.lng);
    return Number.isFinite(lat) && Number.isFinite(lng)
      && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180
      ? { lat, lng }
      : null;
  }

  function formatCoordinate(value) {
    const coordinate = normalizeCoordinate(value);
    return coordinate ? `${coordinate.lat.toFixed(6)}, ${coordinate.lng.toFixed(6)}` : '';
  }

  const fieldLabels = Object.freeze({
    kind: 'Art',
    category: 'Kategorie',
    title: 'Titel',
    coordinate: 'OSM-Geokoordinate',
    description: 'Beschreibung',
    source: 'Quelle',
    page: 'Seitenangabe',
  });

  function effectiveKind(report) {
    return report.proposed.kind || report.original.kind || 'Eintrag';
  }

  function buildReportSubject(report) {
    const reference = report.entryId ? ` ${report.entryId}` : '';
    const prefix = report.mode === 'new' ? 'Vorschlag' : 'Korrektur';
    const title = report.proposed.title || report.original.title || 'Ohne Titel';
    return `[SR6 Maps][${prefix}][${report.city}][${effectiveKind(report)}${reference}] ${title}`;
  }

  function appendDataBlock(rows, heading, data, emptyLabel = 'Nicht angegeben') {
    rows.push(heading);
    Object.entries(fieldLabels).forEach(([key, label]) => {
      rows.push(`${label}: ${asString(data[key]) || emptyLabel}`);
    });
  }

  function buildReportText(report) {
    const rows = [
      'Shadowrun 6 Maps – Community-Korrekturhinweis',
      '',
      `Meldung: ${report.mode === 'new' ? 'Neuen Eintrag vorschlagen' : 'Fehlerhaften Eintrag korrigieren'}`,
      `Stadt/Karte: ${report.city}`,
    ];
    if (report.mode === 'new') {
      rows.push('');
      appendDataBlock(rows, 'Vorgeschlagener Eintrag:', report.proposed);
    } else {
      rows.push(`Eintrags-ID: ${report.entryId || 'Nicht vorhanden'}`, '');
      appendDataBlock(rows, 'Originaldaten:', report.original);
      rows.push('', 'Vorgeschlagene Änderungen:');
      const changes = Object.entries(fieldLabels)
        .filter(([key]) => asString(report.proposed[key]))
        .map(([key, label]) => `${label}: ${asString(report.proposed[key])}`);
      rows.push(...(changes.length ? changes : ['Keine Änderungswerte angegeben.']));
    }
    rows.push(
      '',
      `Kartenlink: ${report.permalink}`,
      `Datenstand: ${report.dataVersion}`,
      '',
      'Hinweis: Diese Meldung wurde in der Web-App vorbereitet und erst durch den Absender im E-Mail-Programm versendet.',
    );
    return rows.join('\n');
  }

  function buildMailtoHref(email, report) {
    return `mailto:${asString(email)}?subject=${encodeURIComponent(buildReportSubject(report))}&body=${encodeURIComponent(buildReportText(report))}`;
  }

  async function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }
    const field = document.createElement('textarea');
    field.value = value;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.appendChild(field);
    field.select();
    const copied = document.execCommand('copy');
    field.remove();
    if (!copied) throw new Error('Kopieren wurde vom Browser abgelehnt.');
  }

  function create(options) {
    const dialog = document.getElementById(options.dialogId || 'report-dialog');
    const form = document.getElementById(options.formId || 'report-form');
    if (!dialog || !form) throw new Error('Das Korrekturformular konnte nicht initialisiert werden.');

    const fields = {
      kind: document.getElementById('report-kind'),
      entryId: document.getElementById('report-entry-id'),
      category: document.getElementById('report-category'),
      title: document.getElementById('report-title'),
      coordinate: document.getElementById('report-coordinate'),
      description: document.getElementById('report-description'),
      source: document.getElementById('report-source'),
      page: document.getElementById('report-page'),
    };
    const originalFields = {
      kind: document.getElementById('report-original-kind'),
      entryId: document.getElementById('report-original-entry-id'),
      category: document.getElementById('report-original-category'),
      title: document.getElementById('report-original-title-value'),
      coordinate: document.getElementById('report-original-coordinate'),
      description: document.getElementById('report-original-description'),
      source: document.getElementById('report-original-source'),
      page: document.getElementById('report-original-page'),
    };
    const status = document.getElementById('report-status');
    const recipient = document.getElementById('report-recipient');
    const emailButton = document.getElementById('report-email');
    const originalPanel = document.getElementById('report-original-data');
    const entryIdField = document.getElementById('report-entry-id-field');
    const email = asString(options.email);
    const emailConfigured = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    const editableFields = ['kind', 'category', 'title', 'coordinate', 'description', 'source', 'page'];
    let context = null;
    let lastFocus = null;

    const setStatus = (message, state = '') => {
      status.textContent = message;
      status.dataset.state = state;
    };

    const proposedData = () => ({
      kind: fields.kind.value,
      category: fields.category.value.trim(),
      title: fields.title.value.trim(),
      coordinate: fields.coordinate.value ? formatCoordinate(fields.coordinate.value) : '',
      description: fields.description.value.trim(),
      source: fields.source.value.trim(),
      page: fields.page.value.trim(),
    });

    const currentReport = () => ({
      mode: context.mode,
      city: options.cityLabel,
      entryId: fields.entryId.value,
      original: { ...context.original },
      proposed: proposedData(),
      permalink: context.permalink || window.location.href,
      dataVersion: options.dataVersion || 'nicht angegeben',
    });

    const formIsReady = () => {
      if (!context) return false;
      const values = Object.fromEntries(editableFields.map(name => [name, fields[name].value.trim()]));
      if (values.coordinate && !normalizeCoordinate(values.coordinate)) return false;
      return context.mode === 'new'
        ? editableFields.every(name => Boolean(values[name]))
        : editableFields.some(name => Boolean(values[name]));
    };

    const syncEmailButton = () => {
      const ready = formIsReady();
      emailButton.disabled = !ready;
      if (!ready) {
        emailButton.title = context && context.mode === 'new'
          ? 'Bitte fülle zuerst alle Pflichtfelder aus.'
          : 'Bitte trage zuerst mindestens einen korrigierten Wert ein.';
      } else if (!emailConfigured) {
        emailButton.title = 'Die Projektadresse ist noch nicht konfiguriert.';
      } else {
        emailButton.title = '';
      }
      emailButton.setAttribute('aria-disabled', ready ? 'false' : 'true');
    };

    const validate = () => {
      const coordinate = fields.coordinate.value.trim();
      fields.coordinate.setCustomValidity(coordinate && !normalizeCoordinate(coordinate)
        ? 'Bitte gib eine gültige Koordinate als Breitengrad, Längengrad ein.'
        : '');
      fields.description.setCustomValidity('');
      if (context.mode === 'correction') {
        const hasChange = editableFields.some(name => fields[name].value.trim());
        if (!hasChange) fields.description.setCustomValidity('Bitte trage mindestens einen korrigierten Wert ein.');
      }
      return form.reportValidity();
    };

    const updateCoordinate = value => {
      fields.coordinate.value = formatCoordinate(value);
      fields.coordinate.setCustomValidity('');
      setStatus(fields.coordinate.value
        ? 'Koordinate übernommen. Die E-Mail wird erst nach deiner Bestätigung im E-Mail-Programm versendet.'
        : 'Bitte wähle eine Position auf der Karte.', fields.coordinate.value ? 'success' : '');
      syncEmailButton();
    };

    const open = nextContext => {
      const mode = nextContext.mode === 'new' || nextContext.kind === 'Neuer Ort' ? 'new' : 'correction';
      const original = {
        kind: mode === 'new' ? '' : asString(nextContext.kind),
        category: mode === 'new' ? '' : asString(nextContext.category),
        title: mode === 'new' ? '' : asString(nextContext.title),
        coordinate: mode === 'new' ? '' : formatCoordinate(nextContext.originalCoordinate),
        description: mode === 'new' ? '' : asString(nextContext.description),
        source: mode === 'new' ? '' : asString(nextContext.source),
        page: mode === 'new' ? '' : asString(nextContext.page),
      };
      context = { ...nextContext, mode, original };
      lastFocus = document.activeElement;
      form.reset();
      fields.entryId.value = mode === 'new' ? '' : asString(nextContext.entryId);
      fields.kind.options[0].textContent = mode === 'new'
        ? 'Bitte auswählen'
        : `Unverändert (${original.kind || 'Eintrag'})`;
      editableFields.forEach(name => { fields[name].required = mode === 'new'; });
      fields.category.placeholder = mode === 'new' ? 'Kategorie' : original.category;
      fields.title.placeholder = mode === 'new' ? 'Titel' : original.title;
      fields.coordinate.placeholder = mode === 'new' ? 'Breitengrad, Längengrad' : original.coordinate;
      fields.description.placeholder = mode === 'new' ? 'Beschreibung des neuen Eintrags' : original.description;
      fields.source.placeholder = mode === 'new' ? 'Titel des Quellenbuchs' : original.source;
      fields.page.placeholder = mode === 'new' ? 'z. B. S. 42–43' : original.page;
      if (mode === 'new') updateCoordinate(nextContext.coordinate);
      originalFields.kind.textContent = original.kind || '–';
      originalFields.entryId.textContent = asString(nextContext.entryId) || '–';
      originalFields.category.textContent = original.category || '–';
      originalFields.title.textContent = original.title || '–';
      originalFields.coordinate.textContent = original.coordinate || '–';
      originalFields.description.textContent = original.description || '–';
      originalFields.source.textContent = original.source || '–';
      originalFields.page.textContent = original.page || '–';
      originalPanel.hidden = mode === 'new';
      entryIdField.hidden = mode === 'new' || !fields.entryId.value;
      document.getElementById('report-dialog-title').textContent = mode === 'new'
        ? 'Neuen Eintrag vorschlagen'
        : 'Fehlerhaften Eintrag melden';
      document.getElementById('report-form-title').textContent = mode === 'new'
        ? 'Daten des neuen Eintrags'
        : 'Korrigierte Daten';
      document.getElementById('report-context-city').textContent = options.cityLabel;
      document.getElementById('report-context-entry').textContent = mode === 'new'
        ? 'Neuer Eintrag'
        : nextContext.entryId ? `${nextContext.entryId} · ${nextContext.title}` : nextContext.title;
      setStatus(mode === 'new'
        ? 'Alle Felder sind Pflichtfelder. Es wird nichts automatisch versendet.'
        : 'Trage nur die Werte ein, die korrigiert werden sollen. Es wird nichts automatisch versendet.');
      syncEmailButton();
      dialog.hidden = false;
      window.requestAnimationFrame(() => (mode === 'new' ? fields.kind : fields.category).focus());
    };

    const suspend = () => { dialog.hidden = true; };
    const resume = () => {
      if (!context) return;
      dialog.hidden = false;
      window.requestAnimationFrame(() => fields.coordinate.focus());
    };
    const close = () => {
      dialog.hidden = true;
      context = null;
      fields.coordinate.setCustomValidity('');
      fields.description.setCustomValidity('');
      setStatus('Beim Öffnen der E-Mail wird noch nichts versendet.');
      if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
    };

    document.getElementById('report-close').addEventListener('click', close);
    document.getElementById('report-cancel').addEventListener('click', close);
    dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
    document.getElementById('report-pick-coordinate').addEventListener('click', () => {
      if (typeof options.onPickCoordinate === 'function') options.onPickCoordinate();
    });
    editableFields.forEach(name => {
      fields[name].addEventListener('input', syncEmailButton);
      fields[name].addEventListener('change', syncEmailButton);
    });
    document.getElementById('report-copy-coordinate').addEventListener('click', async () => {
      const coordinate = fields.coordinate.value || fields.coordinate.placeholder;
      if (!coordinate) {
        setStatus('Es ist noch keine Koordinate vorhanden.', 'error');
        return;
      }
      try {
        await copyText(coordinate);
        setStatus('Koordinate kopiert.', 'success');
      } catch (error) {
        setStatus(error.message, 'error');
      }
    });
    document.getElementById('report-copy').addEventListener('click', async () => {
      if (!validate()) return;
      try {
        await copyText(buildReportText(currentReport()));
        setStatus('Vollständige Meldung kopiert.', 'success');
      } catch (error) {
        setStatus(error.message, 'error');
      }
    });
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!validate()) return;
      if (!emailConfigured) {
        setStatus('Die Projektadresse ist noch nicht konfiguriert. Nutze vorerst „Meldung kopieren“.', 'error');
        return;
      }
      setStatus('Das E-Mail-Programm wird geöffnet. Die Meldung wird noch nicht automatisch versendet.', 'success');
      window.location.href = buildMailtoHref(email, currentReport());
    });

    recipient.textContent = emailConfigured ? email : 'Projektadresse noch nicht konfiguriert';
    syncEmailButton();

    return {
      open,
      close,
      suspend,
      resume,
      updateCoordinate,
      isOpen: () => !dialog.hidden,
      hasContext: () => Boolean(context),
      buildCurrentReport: currentReport,
    };
  }

  window.SR6CorrectionReports = {
    create,
    formatCoordinate,
    buildReportSubject,
    buildReportText,
    buildMailtoHref,
    copyText,
  };
})();

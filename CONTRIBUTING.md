# Katkıda Bulunma Rehberi / Contributing Guide

Bu projeye katkıda bulunmak istediğiniz için teşekkürler!  
(*Thank you for your interest in contributing!*)

---

## 🇹🇷 Türkçe

### Katkı Türleri

- **Hata bildirimi (Bug Report)**: [Issues](https://github.com/Xtra01/ppt-to-kvkk-analyzer/issues) sayfasını kullanın
- **Özellik isteği (Feature Request)**: Issues → "feature_request" şablonu
- **Pull Request**: Aşağıdaki süreci takip edin

### Geliştirme Ortamı

```bash
git clone https://github.com/Xtra01/ppt-to-kvkk-analyzer.git
cd ppt-to-kvkk-analyzer

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"    # Geliştirici bağımlılıkları
```

### Kod Standartları

- **Biçimlendirici**: `ruff format src/`
- **Linter**: `ruff check src/`
- **Tip kontrolü**: `mypy src/`
- **Test**: `pytest`

### Pull Request Süreci

1. `main`'den fork edin
2. Yeni bir dal (branch) açın: `feature/ozellik-adi` veya `fix/hata-adi`
3. Değişikliklerinizi yapın ve commit edin (geleneksel commit mesajı: `feat:`, `fix:`, `docs:`)
4. `CHANGELOG.md`'yi güncelleyin
5. Pull Request açın

### Lisans Uyarısı

PR göndererek projede uygulanan [CC BY-NC 4.0](LICENSE) lisans koşullarını  
kabul etmiş sayılırsınız. Ticari katkılar için önce yazara başvurun.

---

## 🇬🇧 English

### How to Contribute

1. **Report bugs** via [Issues](https://github.com/Xtra01/ppt-to-kvkk-analyzer/issues)
2. **Request features** via the feature_request template
3. **Submit Pull Requests** following the process above

### Code Style

- Formatter: `ruff format`
- Linter: `ruff check`
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`

### License Note

By submitting a PR, you agree that your contributions will be licensed under [CC BY-NC 4.0](LICENSE).

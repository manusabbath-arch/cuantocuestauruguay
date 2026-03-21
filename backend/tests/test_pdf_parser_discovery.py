from app.etl import pdf_parser


class MockResponse:
    def __init__(self, text="", content=b"", status_code=200):
        self.text = text
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}")


def test_discover_latest_pdf_url_prioritizes_keywords_and_year(monkeypatch):
    html = """
    <html>
      <body>
        <a href="/docs/boletin_2023.pdf">Boletin 2023</a>
        <a href="/docs/pliego_tarifario_ute_2025.pdf">Pliego Tarifario UTE 2025</a>
        <a href="/docs/informe_general_2026.pdf">Informe general 2026</a>
      </body>
    </html>
    """

    monkeypatch.setattr(
        "app.etl.pdf_parser.requests.get",
        lambda *_args, **_kwargs: MockResponse(text=html),
    )

    selected = pdf_parser.discover_latest_pdf_url(
        "https://www.ursea.gub.uy/inicio/energia-electrica/tarifas/",
        preferred_keywords=["ute", "pliego", "tarifario"],
    )

    assert selected is not None
    assert selected.endswith("pliego_tarifario_ute_2025.pdf")


def test_download_pdf_saves_content(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.etl.pdf_parser.requests.get",
        lambda *_args, **_kwargs: MockResponse(content=b"%PDF-sample"),
    )

    file_path = pdf_parser.download_pdf(
        "https://www.ursea.gub.uy/docs/pliego_tarifario_ute_2025.pdf",
        str(tmp_path),
        "ute_tarifas_latest",
    )

    assert file_path is not None
    assert file_path.endswith("pliego_tarifario_ute_2025.pdf")
    assert (tmp_path / "pliego_tarifario_ute_2025.pdf").read_bytes() == b"%PDF-sample"

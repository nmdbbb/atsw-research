"""Cong CI: ledger phai xac nhan duoc, va moi ghim sha256 phai byte-exact.

Test nay bat lai dung loi da xay ra: ban ghi duoc tao tren Windows voi CRLF, git
chuan hoa khi checkout tren Linux, digest() bam byte tho nen hash lech -> verify_ledger
fail tren mot nen tang va pass tren nen tang kia.
"""
import hashlib, pathlib, sys, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import workflow as W                      # noqa: E402
import verify_hash_pins as VHP            # noqa: E402


class LedgerVerifies(unittest.TestCase):
    def test_ledger_chain_and_contract(self):
        self.assertEqual(W.verify_contract(ROOT)["objective_id"],
                         W.read_json(ROOT / "objective.json")["id"])

    def test_every_hash_pin_is_byte_exact(self):
        _rows, _counts, bad = VHP.report()
        self.assertEqual(bad, [], "ghim hash khong khop: %s" % bad)

    def test_gitattributes_disables_eol_normalisation(self):
        ga = ROOT.parent / ".gitattributes"
        self.assertTrue(ga.is_file(), ".gitattributes bi thieu o goc repo")
        self.assertIn("* -text", ga.read_text(encoding="utf-8"))

    def test_digest_is_byte_exact_not_normalised(self):
        """Neu ai do doi digest() sang chuan hoa ket thuc dong thi hash da commit vo."""
        p = ROOT / "tests" / "_eol_probe.tmp"
        try:
            p.write_bytes(b"a\r\nb\r\n")
            crlf = W.digest(p)
            p.write_bytes(b"a\nb\n")
            self.assertNotEqual(crlf, W.digest(p))
        finally:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

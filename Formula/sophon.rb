class Sophon < Formula
  desc "Run Sophon locally — Claude Code session metrics dashboard"
  homepage "https://github.com/sophon-data/sophon"
  url "https://github.com/sophon-data/homebrew-sophon.git", branch: "main"
  version "0.1.0"
  license "Proprietary"

  def install
    bin.install "bin/sophon"
    (etc/"sophon").install "share/docker-compose.yml"
  end

  def caveats
    <<~EOS
      Sophon needs Docker Desktop running:
        https://www.docker.com/products/docker-desktop

      One-time auth (Sophon images are private on GHCR):
        sophon login

      Then:
        sophon start
    EOS
  end

  test do
    assert_match "sophon — run Sophon locally", shell_output("#{bin}/sophon --help")
  end
end

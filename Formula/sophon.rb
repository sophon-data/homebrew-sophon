class Sophon < Formula
  desc "Run Sophon locally — Claude Code session metrics dashboard"
  homepage "https://github.com/sophon-data/sophon"
  url "https://github.com/sophon-data/homebrew-sophon.git", branch: "main"
  version "0.1.0"
  license "Proprietary"

  depends_on "python@3.13"

  def install
    bin.install "bin/sophon"
    libexec.install "libexec/sophon_login"
    (etc/"sophon").install "share/docker-compose.yml"
  end

  def caveats
    <<~EOS
      Sophon needs Docker Desktop running:
        https://www.docker.com/products/docker-desktop

      To sign in and start the app:
        sophon login

      Other commands:
        sophon logout     sign out
        sophon stop       stop the app
        sophon uninstall  remove all local data
    EOS
  end

  test do
    assert_match "sophon — run Sophon locally", shell_output("#{bin}/sophon --help")
  end
end

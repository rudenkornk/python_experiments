{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-25.11";
    };
    nur = {
      url = "github:nix-community/nur";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs:
    let
      system = "x86_64-linux";
      pkgs = import inputs.nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          # Bootstrap python & python packages.
          python314
          uv

          # Format & lint tools.
          git
          gitleaks
          markdownlint-cli2
          nixfmt
          prettier
          ruff
          shellcheck
          shfmt
          statix
          stylua
          typos
        ];

        shellHook = ''
          uv sync
          source .venv/bin/activate
          echo "Welcome to the project devshell!"
        '';
      };
    };
}

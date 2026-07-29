{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };
    nur = {
      url = "github:nix-community/nur";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
      python = pkgs.python3;
      pythonPkgs = python.pkgs;

      pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
      inherit (pyproject) project;

      dependencies = map (
        dep: pythonPkgs.${builtins.head (builtins.split "(==|>=|<=|!=|~=|>|<)" dep)}
      ) project.dependencies;

      testDependencies = with pythonPkgs; [
        pytest
        pytest-asyncio
        pytest-cov
        pytest-xdist
      ];

      lintDependencies = with pkgs; [
        # Format & lint tools.
        git
        gitleaks
        markdownlint-cli2
        mdformat
        mypy
        nixfmt
        prettier
        pythonPkgs.mdformat
        pythonPkgs.mdformat-beautysh
        pythonPkgs.mdformat-gfm
        ruff
        shellcheck
        shfmt
        statix
        stylua
        typos
        yamllint
      ];

    in
    {
      packages.${system}.default = pythonPkgs.buildPythonPackage {
        pyproject = true;
        pname = project.name;
        inherit (project) version;

        src = ./.;

        inherit dependencies;

        build-system = [ pythonPkgs.hatchling ];

        meta = {
          inherit (project) description;
          mainProgram = project.name;
          license = pkgs.lib.licenses.mit;
        };

        pythonImportsCheck = [ project.name ];

        nativeCheckInputs = [ pythonPkgs.pytestCheckHook ] ++ testDependencies;

        # Disable coverage during nix build since the sandbox is read-only
        pytestFlags = [ "--no-cov" ];
      };

      devShells.${system}.default = pkgs.mkShell {
        packages = [ python ] ++ dependencies ++ testDependencies ++ lintDependencies;
        shellHook = ''
          export PYTHONPATH="$PWD/src:$PWD:$PYTHONPATH"
          export IN_NIX_SHELL=impure
          # `$PWD` puts the repo root on PYTHONPATH so the interpreter imports `sitecustomize.py`,
          # which starts coverage in subprocesses.
          # See that file for why coverage's `patch = ["subprocess"]` cannot replace it here.
          export COVERAGE_PROCESS_START="$PWD/pyproject.toml"
          echo "Welcome to the project devshell!"
        '';
      };
    };
}

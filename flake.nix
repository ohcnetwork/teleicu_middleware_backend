{
  description = "Minimal flake for teleicu_middleware_backend";

  outputs = { self, nixpkgs, ... }: {
    packages.default = nixpkgs.lib.makeDerivation {
      name = "teleicu_middleware_backend";
      src = ./.;
    };
  };
}

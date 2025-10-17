{ pkgs, ... }: {
  channel = "stable-24.05";
  
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
  ];
  
  idx = {
    extensions = [ "ms-python.python" ];
    
    workspace = {
      onCreate = {
        setup = ''
          python -m venv .venv
          source .venv/bin/activate
          pip install --upgrade pip
          pip install flask flask-cors requests
        '';
      };
      
      onStart = {
        activate = "source .venv/bin/activate";
      };
    };
    
    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "sh"
            "-c"
            "source .venv/bin/activate && python main.py"
          ];
          manager = "web";
          env = {
            PORT = "$PORT";
          };
        };
      };
    };
  };
}
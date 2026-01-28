const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

function runPython(text, mode) {
  const py = process.platform === 'win32' ? 'python' : 'python3';
  const script = path.join(__dirname, 'python', 'anon.py');
  const res = cp.spawnSync(py, [script, mode], {
    input: text,
    encoding: 'utf-8'
  });
  return res.stdout || text;
}

exports.activate = (context) => {
  function setHistoryFlag() {
    vscode.commands.executeCommand('setContext','anonimizacja.hasHistory',true);
  }

  context.subscriptions.push(
    vscode.commands.registerCommand('anonimizacja.runFile', () => {
      const e = vscode.window.activeTextEditor;
      if (!e) return;
      const t = e.document.getText();
      e.edit(b => b.replace(
        new vscode.Range(e.document.positionAt(0), e.document.positionAt(t.length)),
        runPython(t,'anon')
      ));
      setHistoryFlag();
    }),

    vscode.commands.registerCommand('anonimizacja.runSelection', () => {
      const e = vscode.window.activeTextEditor;
      if (!e || e.selection.isEmpty) return;
      e.edit(b => b.replace(e.selection,
        runPython(e.document.getText(e.selection),'anon')
      ));
      setHistoryFlag();
    }),

    vscode.commands.registerCommand('anonimizacja.reverseSelection', () => {
      const e = vscode.window.activeTextEditor;
      if (!e || e.selection.isEmpty) return;
      e.edit(b => b.replace(e.selection,
        runPython(e.document.getText(e.selection),'reverse')
      ));
    })
  );
};
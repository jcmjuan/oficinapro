<!--
  OficinaPro v1.0 — roteiro da apresentação final.
  Cada bloco entre os marcadores SLIDE vira uma página 16:9 no PDF.
  Imagens: docs/final/capturas/ e docs/etapa2/diagramas/.
-->

<div class="slide cover">
  <div class="cover-logo"><img src="../../assets/logo-horizontal.png" alt="DevSolo Studio — OficinaPro"></div>
  <div class="cover-main">
    <div class="kicker">AVALIAÇÃO G2 • ETAPA FINAL • 19/11/2026</div>
    <h1>OficinaPro <span>v1.0</span></h1>
    <p class="cover-sub">Interface, integração e entrega final</p>
    <p class="cover-lead">Do orçamento ao recibo: uma operação completa para a oficina, com PDF, WhatsApp, relatórios e backup.</p>
  </div>
  <div class="cover-meta">
    <div><strong>Equipe</strong><br>DevSolo Studio</div>
    <div><strong>Integrante</strong><br>Juan Carlos Matos</div>
    <div><strong>Stack</strong><br>Python • CustomTkinter • SQLite</div>
  </div>
  <div class="cover-footer">Python 3.12+ • CustomTkinter • SQLite • unittest • Chrome headless</div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Contexto</span><span class="slide-no">02</span></div>
  <h2 class="slide-title">Uma oficina que cresce<br><span>sem perder o controle.</span></h2>
  <div class="grid-2">
    <div class="card muted-card">
      <h3>Antes</h3>
      <ul>
        <li>Orçamentos em planilhas e papéis.</li>
        <li>Histórico do veículo disperso.</li>
        <li>Comissões calculadas à mão.</li>
        <li>PDF e WhatsApp montados manualmente.</li>
      </ul>
    </div>
    <div class="card accent-card">
      <h3>Com o OficinaPro</h3>
      <ul>
        <li>Cadastro único de cliente, veículo e equipe.</li>
        <li>OS com itens, status e histórico auditável.</li>
        <li>Orçamento e recibo em PDF.</li>
        <li>WhatsApp em um clique e relatórios gerenciais.</li>
      </ul>
    </div>
  </div>
  <div class="quote">O núcleo da Etapa 3 virou produto: a mesma regra de negócio, agora com uma experiência completa.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">A entrega</span><span class="slide-no">03</span></div>
  <h2 class="slide-title">O escopo em números.</h2>
  <div class="metric-grid">
    <div class="metric"><strong>7</strong><span>telas</span></div>
    <div class="metric"><strong>9</strong><span>diálogos</span></div>
    <div class="metric"><strong>29</strong><span>testes</span></div>
    <div class="metric"><strong>14</strong><span>fluxos validados</span></div>
    <div class="metric"><strong>20</strong><span>capturas reais</span></div>
    <div class="metric"><strong>14</strong><span>páginas de relatório</span></div>
  </div>
  <div class="grid-3">
    <div class="mini-card"><h3>Núcleo preservado</h3><p>Domínio, SQLite, serviços, PDF e WhatsApp da Etapa 3.</p></div>
    <div class="mini-card"><h3>Interface integrada</h3><p>CustomTkinter consumindo os mesmos serviços, sem regra duplicada.</p></div>
    <div class="mini-card"><h3>Entrega completa</h3><p>Relatório, capturas, slides, seed e instruções de execução.</p></div>
  </div>
  <div class="quote">Uma entrega verificável: 29 testes automatizados e 14 fluxos de interface exercitados.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Arquitetura</span><span class="slide-no">04</span></div>
  <h2 class="slide-title">A interface não recalcula nada.</h2>
  <div class="grid-58-42">
    <div class="shot-card">
      <img src="../etapa2/diagramas/arquitetura.png" alt="Arquitetura em camadas do OficinaPro">
      <p class="caption">Arquitetura preservada da Etapa 2: apresentação → serviços → domínio/repositórios.</p>
    </div>
    <div class="stack">
      <div class="card"><h3>AppContext</h3><p>Monta banco, repositórios e serviços em um único ponto.</p></div>
      <div class="card"><h3>Serviços</h3><p>OS, orçamento, relatórios e configuração concentram as regras.</p></div>
      <div class="card"><h3>Entrada</h3><p><code>python3 main.py</code> abre a UI; <code>--cli</code> preserva o terminal.</p></div>
    </div>
  </div>
  <div class="quote">A dependência aponta sempre para dentro: a interface conhece serviços, não SQL.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Dashboard</span><span class="slide-no">05</span></div>
  <h2 class="slide-title">A operação em uma tela.</h2>
  <div class="grid-62-38">
    <div class="shot-card dashboard">
      <img src="capturas/dashboard.png" alt="Dashboard do OficinaPro">
      <p class="caption">Indicadores do mês, ordens recentes e distribuição por status.</p>
    </div>
    <div class="stack">
      <div class="stat-line"><strong>R$ 18.450</strong><span>faturamento</span></div>
      <div class="stat-line"><strong>R$ 6.320</strong><span>mão de obra</span></div>
      <div class="stat-line"><strong>R$ 743</strong><span>comissões</span></div>
      <p class="small">Os números vêm de <code>RelatorioService</code> e <code>resumo_dashboard()</code>; a tela apenas apresenta.</p>
    </div>
  </div>
  <div class="quote">Indicadores calculados pelos serviços; a interface só organiza a leitura.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Cadastros</span><span class="slide-no">06</span></div>
  <h2 class="slide-title">Clientes e frota, sem retrabalho.</h2>
  <div class="grid-2 shots">
    <div class="shot-card"><img src="capturas/clientes.png" alt="Tela de clientes"><p class="caption">Clientes com busca, situação e acesso à frota.</p></div>
    <div class="shot-card"><img src="capturas/veiculos.png" alt="Tela de veículos"><p class="caption">Frota com última OS, quilometragem e histórico.</p></div>
  </div>
  <div class="pill-row">
    <span class="pill">Busca por nome, placa, documento e e-mail</span>
    <span class="pill">Soft delete com reativação</span>
    <span class="pill">Filtro contextual cliente → veículos</span>
  </div>
  <div class="quote">O mesmo cadastro alimenta a OS, o histórico do veículo e os relatórios.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Operação</span><span class="slide-no">07</span></div>
  <h2 class="slide-title">Da fila ao editor da OS.</h2>
  <div class="grid-2 shots">
    <div class="shot-card"><img src="capturas/ordens.png" alt="Lista de ordens de serviço"><p class="caption">Fila filtrável por status e busca textual.</p></div>
    <div class="shot-card"><img src="capturas/editor-os.png" alt="Editor da ordem de serviço"><p class="caption">Itens, desconto, histórico e ações contextuais.</p></div>
  </div>
  <div class="flow">
    <span class="flow-step">Orçamento</span><span class="arrow">→</span>
    <span class="flow-step">Aprovada</span><span class="arrow">→</span>
    <span class="flow-step">Em execução</span><span class="arrow">→</span>
    <span class="flow-step done">Finalizada</span>
    <span class="flow-cancel">Cancelada (com motivo)</span>
  </div>
  <div class="quote">Cada transição é validada pelo domínio e registrada no histórico append-only.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Documentos</span><span class="slide-no">08</span></div>
  <h2 class="slide-title">Orçamento, recibo e WhatsApp.</h2>
  <div class="grid-38-62">
    <div class="shot-card portrait"><img src="capturas/dialogo-documento.png" alt="Prévia do orçamento"><p class="caption">Prévia com identidade visual, itens e totais.</p></div>
    <div class="stack">
      <div class="card"><h3>PDF sob demanda</h3><p>Orçamento em <code>ORCAMENTO</code> e recibo em <code>FINALIZADA</code>.</p></div>
      <div class="card"><h3>WhatsApp em um clique</h3><p>Mensagem pronta com cliente, OS, veículo, itens, total e validade.</p></div>
      <div class="card"><h3>Link <code>wa.me</code></h3><p>Sem API proprietária: abre a conversa no aplicativo ou navegador.</p></div>
      <div class="card"><h3>Recibo automático</h3><p>O título muda quando a OS sai de orçamento e é finalizada.</p></div>
    </div>
  </div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Gestão</span><span class="slide-no">09</span></div>
  <h2 class="slide-title">Relatórios, comissões e backup.</h2>
  <div class="grid-58-42 shots">
    <div class="shot-card"><img src="capturas/relatorios.png" alt="Tela de relatórios"><p class="caption">Faturamento, comissões e composição por período.</p></div>
    <div class="shot-card"><img src="capturas/configuracoes-backup.png" alt="Aba de backup"><p class="caption">Backup e restauração com validação.</p></div>
  </div>
  <div class="pill-row">
    <span class="pill">CSV de comissões</span>
    <span class="pill">Backup do banco</span>
    <span class="pill">Schema e ambiente</span>
    <span class="pill">Equipe e oficina</span>
  </div>
  <div class="quote">Relatórios e backup fecham o ciclo de gestão sem sair da aplicação.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Integração</span><span class="slide-no">10</span></div>
  <h2 class="slide-title">Uma regra, duas interfaces.</h2>
  <div class="grid-55-45">
    <table class="clean-table">
      <thead><tr><th>Ação da UI</th><th>Serviço</th></tr></thead>
      <tbody>
        <tr><td>Criar OS</td><td><code>OrdemServicoService</code></td></tr>
        <tr><td>Adicionar item</td><td><code>adicionar_peca()</code></td></tr>
        <tr><td>Desconto</td><td><code>aplicar_desconto()</code></td></tr>
        <tr><td>Transições</td><td><code>aprovar / iniciar / finalizar</code></td></tr>
        <tr><td>PDF e WhatsApp</td><td><code>OrcamentoService</code></td></tr>
        <tr><td>Relatórios</td><td><code>RelatorioService</code></td></tr>
        <tr><td>Backup</td><td><code>ConfiguracaoService</code></td></tr>
      </tbody>
    </table>
    <div class="stack">
      <div class="code-card"><pre>python3 main.py        # UI
python3 main.py --cli  # terminal
python3 main.py --ui   # força UI</pre></div>
      <div class="card"><h3>Sem duplicação</h3><p>A UI coleta dados e apresenta resultados; o domínio valida e calcula.</p></div>
      <div class="card"><h3>CLI preservado</h3><p>Fallback para ambientes sem Tkinter ou demonstrações headless.</p></div>
    </div>
  </div>
  <div class="quote">A mesma regra sustenta a interface, o terminal e os testes automatizados.</div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Qualidade</span><span class="slide-no">11</span></div>
  <h2 class="slide-title">Validado, não só compilado.</h2>
  <div class="metric-grid small-metrics">
    <div class="metric"><strong>29</strong><span>testes OK</span></div>
    <div class="metric"><strong>14</strong><span>fluxos de UI</span></div>
    <div class="metric"><strong>0</strong><span>erros de compilação</span></div>
    <div class="metric"><strong>7</strong><span>telas exercitadas</span></div>
  </div>
  <div class="grid-2">
    <div class="card">
      <h3>Roteiro de integração</h3>
      <ul class="check-list">
        <li>Cliente, veículo e mecânico</li>
        <li>OS, peças, mão de obra e desconto</li>
        <li>Aprovação, execução e finalização</li>
        <li>PDF, WhatsApp e cancelamento</li>
        <li>CSV, backup e restauração</li>
      </ul>
    </div>
    <div class="card">
      <h3>Ambiente da validação</h3>
      <p>Python 3.14.4 • Tk 8.6 • CustomTkinter 6.0.0</p>
      <p>Janela 1440 × 900 • capturas reais em <code>docs/final/capturas/</code></p>
      <p class="small">O roteiro criou as OS 2026-0043 e 2026-0044 em banco temporário, sem alterar a base demonstrativa.</p>
    </div>
  </div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Demonstração</span><span class="slide-no">12</span></div>
  <h2 class="slide-title">Um roteiro de cinco minutos.</h2>
  <div class="demo-grid">
    <div class="demo-step"><span>01</span><h3>Abrir a OS</h3><p>Cliente, veículo e responsável.</p></div>
    <div class="demo-step"><span>02</span><h3>Adicionar itens</h3><p>Peça e mão de obra com totais.</p></div>
    <div class="demo-step"><span>03</span><h3>Concluir</h3><p>Aprovar, iniciar e finalizar.</p></div>
    <div class="demo-step"><span>04</span><h3>Enviar</h3><p>PDF e WhatsApp em um clique.</p></div>
    <div class="demo-step"><span>05</span><h3>Gerir</h3><p>Relatório, CSV e backup.</p></div>
  </div>
  <div class="quote">A demonstração percorre o mesmo caminho do cliente: orçamento → aprovação → execução → recibo.</div>
  <div class="grid-3" style="margin-top:16px">
    <div class="mini-card"><h3>OS finalizada</h3><p>Histórico e quilometragem atualizados.</p></div>
    <div class="mini-card"><h3>PDF gerado</h3><p>Documento pronto para envio.</p></div>
    <div class="mini-card"><h3>WhatsApp aberto</h3><p>Mensagem com o resumo da OS.</p></div>
  </div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide">
  <div class="slide-head"><span class="kicker">Roadmap</span><span class="slide-no">13</span></div>
  <h2 class="slide-title">O que fica para a próxima versão.</h2>
  <div class="grid-2">
    <div class="card muted-card">
      <h3>Limitações atuais</h3>
      <ul>
        <li>Aplicação desktop local, sem autenticação.</li>
        <li>Comissões informativas, sem baixa financeira.</li>
        <li>PDF depende de Chrome/Chromium headless.</li>
        <li>Sem estoque, agenda ou emissão fiscal.</li>
      </ul>
    </div>
    <div class="card accent-card">
      <h3>Próximos passos</h3>
      <ul>
        <li>Pagamento de comissões e fechamento financeiro.</li>
        <li>Estoque de peças e alertas de mínimo.</li>
        <li>Agenda de serviços e previsão de entrega.</li>
        <li>Empacotamento com PyInstaller e autenticação.</li>
      </ul>
    </div>
  </div>
  <div class="quote">A base está pronta: o próximo ciclo é de profundidade operacional, não de reconstrução.</div>
  <div class="flow" style="margin-top:18px">
    <span class="flow-step done">v1.0 entrega</span><span class="arrow">→</span>
    <span class="flow-step">v1.1 financeiro</span><span class="arrow">→</span>
    <span class="flow-step">v1.2 estoque/agenda</span><span class="arrow">→</span>
    <span class="flow-step">v2.0 distribuição</span>
  </div>
  <div class="slide-footer"><span>OficinaPro v1.0</span><span>DevSolo Studio</span></div>
</div>

<!-- SLIDE -->

<div class="slide dark closing">
  <div class="slide-head"><span class="kicker">Conclusão</span><span class="slide-no">14</span></div>
  <h2 class="closing-title">Contrato cumprido.<br><span>Pronto para operar.</span></h2>
  <div class="closing-grid">
    <div><strong>Núcleo</strong><p>Domínio, SQLite, serviços e testes.</p></div>
    <div><strong>Interface</strong><p>Sete telas integradas, sem regra duplicada.</p></div>
    <div><strong>Entrega</strong><p>Relatório, capturas, slides e execução.</p></div>
  </div>
  <div class="thanks">Obrigado.<br><span>Perguntas?</span></div>
  <div class="slide-footer"><span>OficinaPro v1.0 • DevSolo Studio</span><span>Juan Carlos Matos • 19/11/2026</span></div>
</div>

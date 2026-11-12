
document.addEventListener('DOMContentLoaded', function () {

    // =====================================================
    // 1. NAVEGAÇÃO ORIGINAL DO SIGAD
    // =====================================================

    const currentPath = window.location.pathname;

    document.querySelectorAll('.nav-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });


    // =====================================================
    // VERIFICAÇÃO DO JQUERY
    // =====================================================

    if (typeof window.jQuery === 'undefined') {
        console.error('SIGAD: jQuery não foi carregado.');
        return;
    }

    const $ = window.jQuery;


    // =====================================================
    // PLUGIN 1: JQUERY MASK
    // Máscaras para CPF e telefone
    // =====================================================

    if ($.fn.mask) {

        // Máscara de CPF: 000.000.000-00
        $('input[name="cpf"], #id_cpf').mask('000.000.000-00');

        // Máscara dinâmica de telefone
        $('input[name="telefone"], #id_telefone').each(function () {

            const telefone = $(this);

            const aplicarMascara = function (valor) {
                return valor.replace(/\D/g, '').length > 10
                    ? '(00) 00000-0000'
                    : '(00) 0000-00009';
            };

            telefone.mask('(00) 0000-00009', {
                onKeyPress: function (valor, evento, campo, opcoes) {
                    campo.mask(aplicarMascara(valor), opcoes);
                }
            });

        });

        console.log('SIGAD: jQuery Mask carregado.');
    }


    // =====================================================
    // PLUGIN 2: DATATABLES
    // Pesquisa e ordenação nas tabelas
    // =====================================================

    if ($.fn.DataTable) {

        $('table.sigad-table').each(function () {

            const tabela = $(this);
            const cabecalho = this.querySelectorAll('thead th').length;
            const corpo = this.querySelector('tbody');

            // Verifica se existe uma tabela válida
            if (!cabecalho || !corpo) {
                return;
            }

            // Ignora tabelas vazias ou com linhas de colspan
            const linhasValidas = Array.from(corpo.rows).filter(function (linha) {
                return linha.cells.length === cabecalho;
            });

            if (linhasValidas.length === 0) {
                return;
            }

            // Evita inicializar a mesma tabela mais de uma vez
            if ($.fn.DataTable.isDataTable(this)) {
                return;
            }

            tabela.DataTable({
                paging: false,
                searching: true,
                ordering: true,
                info: false,
                lengthChange: false,
                autoWidth: false,
                language: {
                    search: 'Pesquisar nesta página:',
                    searchPlaceholder: 'Digite para pesquisar...',
                    zeroRecords: 'Nenhum resultado encontrado.',
                    emptyTable: 'Nenhum registro disponível.',
                    infoEmpty: 'Nenhum registro disponível.',
                    processing: 'Carregando...'
                },
                columnDefs: [
                    {
                        targets: -1,
                        orderable: false
                    }
                ]
            });

        });

        console.log('SIGAD: DataTables carregado.');
    }


    // =====================================================
    // PLUGIN 3: SELECT2
    // Melhora os campos de seleção
    // =====================================================

    if ($.fn.select2) {

        $('select.sigad-input').each(function () {

            const campo = $(this);

            // Evita inicializar o mesmo campo novamente
            if (campo.hasClass('select2-hidden-accessible')) {
                return;
            }

            campo.select2({
                width: '100%',
                placeholder: 'Selecione uma opção...',
                allowClear: !campo.prop('required'),
                language: {
                    noResults: function () {
                        return 'Nenhum resultado encontrado.';
                    },
                    searching: function () {
                        return 'Pesquisando...';
                    }
                }
            });

        });

        console.log('SIGAD: Select2 carregado.');
    }

});

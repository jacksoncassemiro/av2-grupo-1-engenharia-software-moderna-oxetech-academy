import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';

// Sem esse plugin, dayjs(valor, 'DD/MM/YYYY') ignora o formato em silencio e cai no
// parsing nativo do Date() - que interpreta string com barra como MM/DD/YYYY (EUA) e
// troca dia com mes. E o que causava o DateInput exibir 08/12 para quem digitasse 12/08.
dayjs.extend(customParseFormat);

export default dayjs;

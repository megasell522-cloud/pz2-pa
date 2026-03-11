import logging

def setup_logger(name="Transport"):
    """Настройка логгера для записи в консоль и файл"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # Очистка старых обработчиков, чтобы не дублировались записи
    if logger.handlers:
        logger.handlers.clear()
    # Обработчик для вывода в консоль
    h = logging.StreamHandler()
    # Обработчик для записи в файл
    f = logging.FileHandler('transport.log', encoding='utf-8')
    # Формат сообщений: дата-время - уровень - сообщение
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    h.setFormatter(fmt)
    f.setFormatter(fmt)
    logger.addHandler(h)
    logger.addHandler(f)
    return logger

class TransportSolver:
    """Класс для решения задачи выбора оптимальной стратегии"""
    
    def __init__(self, log):
        self.log = log
        self.matrix = []      # Матрица выигрышей
        self.strategies = []  # Названия стратегий
        self.states = []      # Названия состояний спроса
    
    def set_data(self, matrix, strategies, states):
        """Установка исходных данных задачи"""
        self.matrix, self.strategies, self.states = matrix, strategies, states
        self.log.info("="*60)
        self.log.info("ЗАДАЧА: Выбор уровня провозных возможностей")
        self.log.info("Стратегии: {}".format(strategies))
        self.log.info("Состояния: {}".format(states))
        self.log.info("Матрица выигрышей:")
        # Вывод матрицы построчно
        for i, s in enumerate(strategies):
            self.log.info("  {}: {}".format(s, matrix[i]))
    
    def wald(self):
        """
        Критерий Вальда (максимин)
        Выбираем стратегию с максимальным минимальным выигрышем
        Позиция: крайний пессимизм, гарантия результата
        """
        self.log.info("\n--- КРИТЕРИЙ ВАЛЬДА (максимин) ---")
        # Находим минимальный выигрыш для каждой стратегии
        mins = [min(row) for row in self.matrix]
        for i, m in enumerate(mins):
            self.log.info("  {}: min = {}".format(self.strategies[i], m))
        # Выбираем стратегию с максимальным из минимальных значений
        idx = mins.index(max(mins))
        self.log.info("Выбор: {} (гарантировано: {})".format(self.strategies[idx], mins[idx]))
        return idx, mins[idx]
    
    def savage(self):
        """
        Критерий Сэвиджа (минимаксный риск)
        Минимизируем максимальные потери (сожаления)
        Риск = лучший результат в столбце - фактический результат
        """
        self.log.info("\n--- КРИТЕРИЙ СЭВИДЖА (минимакс риска) ---")
        # Находим максимальный выигрыш в каждом столбце (по состояниям)
        max_cols = [max(self.matrix[i][j] for i in range(len(self.matrix))) 
                    for j in range(len(self.matrix[0]))]
        # Строим матрицу рисков (сожалений)
        risks = [[max_cols[j] - self.matrix[i][j] for j in range(len(self.matrix[0]))] 
                 for i in range(len(self.matrix))]
        self.log.info("Матрица рисков:")
        for i, s in enumerate(self.strategies):
            self.log.info("  {}: {}".format(s, risks[i]))
        # Находим максимальный риск для каждой стратегии
        max_risks = [max(row) for row in risks]
        for i, r in enumerate(max_risks):
            self.log.info("  {}: max risk = {}".format(self.strategies[i], r))
        # Выбираем стратегию с минимальным максимальным риском
        idx = max_risks.index(min(max_risks))
        self.log.info("Выбор: {} (риск: {})".format(self.strategies[idx], max_risks[idx]))
        return idx, max_risks[idx]
    
    def hurwicz(self, alpha=0.6):
        """
        Критерий Гурвица (взвешенный пессимизм-оптимизм)
        H = alpha * min + (1-alpha) * max
        alpha=1 - полный пессимизм, alpha=0 - полный оптимизм
        """
        self.log.info("\n--- КРИТЕРИЙ ГУРВИЦА (alpha={}) ---".format(alpha))
        # Рассчитываем критерий Гурвица для каждой стратегии
        vals = [alpha*min(row) + (1-alpha)*max(row) for row in self.matrix]
        for i, (s, v) in enumerate(zip(self.strategies, vals)):
            self.log.info("  {}: H = {:.2f}".format(s, v))
        # Выбираем стратегию с максимальным значением H
        idx = vals.index(max(vals))
        self.log.info("Выбор: {} (H = {:.2f})".format(self.strategies[idx], vals[idx]))
        return idx, vals[idx]
    
    def solve(self):
        """Запуск всех критериев и вывод итоговых результатов"""
        self.log.info("="*60)
        w_idx, _ = self.wald()      # Критерий Вальда
        s_idx, _ = self.savage()    # Критерий Сэвиджа
        h_idx, _ = self.hurwicz()   # Критерий Гурвица
        
        self.log.info("\n" + "="*60)
        self.log.info("РЕЗУЛЬТАТЫ:")
        self.log.info("  Вальда:    {}".format(self.strategies[w_idx]))
        self.log.info("  Сэвиджа:   {}".format(self.strategies[s_idx]))
        self.log.info("  Гурвица:   {}".format(self.strategies[h_idx]))
        
        # Проверяем, совпадают ли рекомендации всех критериев
        if w_idx == s_idx == h_idx:
            self.log.info("\n*** ВСЕ КРИТЕРИИ: {} ***".format(self.strategies[w_idx]))
        else:
            self.log.info("\nРекомендации различаются!")
        self.log.info("="*60)

def main():
    """Основная функция программы"""
    # Создаём и настраиваем логгер
    log = setup_logger()
    log.info("Старт программы")
    
    # Создаём решатель
    solver = TransportSolver(log)
    # Устанавливаем данные задачи
    solver.set_data(
        # Матрица выигрышей (прибыль в тыс. руб.)
        # Строки: стратегии (уровни возможностей)
        # Столбцы: состояния (уровни спроса)
        matrix=[[50, 60, 70], [30, 80, 90], [10, 70, 120], [-20, 50, 150]],
        strategies=["Низкий", "Средний", "Высокий", "Макс"],
        states=["Низкий спрос", "Средний спрос", "Высокий спрос"]
    )
    # Решаем задачу всеми критериями
    solver.solve()
    log.info("Завершение")

if __name__ == "__main__":
    main()
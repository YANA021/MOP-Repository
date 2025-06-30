from django.test import SimpleTestCase

from .solver import resolver_problema_lineal


class SolverTestCase(SimpleTestCase):
    """Pruebas para el solucionador por método gráfico."""

    def test_solucion_optima(self):
        """Problema con única solución óptima devuelve los valores correctos."""
        restricciones = [
            {"coef_x1": 2, "coef_x2": 1, "operador": "<=", "valor": 18},
            {"coef_x1": 2, "coef_x2": 3, "operador": "<=", "valor": 42},
            {"coef_x1": 3, "coef_x2": 1, "operador": "<=", "valor": 24},
        ]
        res = resolver_problema_lineal("max", 3, 2, restricciones)
        self.assertEqual(res["status"], "optimo")
        self.assertAlmostEqual(res["x"], 3.0)
        self.assertAlmostEqual(res["y"], 12.0)
        self.assertAlmostEqual(res["z"], 33.0)

    def test_solucion_no_acotada(self):
        """Detecta problemas con soluciones no acotadas."""
        restricciones = [
            {"coef_x1": 1, "coef_x2": -1, "operador": ">=", "valor": 1},
        ]
        res = resolver_problema_lineal("max", 1, 1, restricciones)
        self.assertEqual(res["status"], "no acotada")

    def test_soluciones_multiples(self):
        """Detecta problemas con soluciones óptimas múltiples."""
        restricciones = [
            {"coef_x1": 1, "coef_x2": 1, "operador": "<=", "valor": 2},
        ]
        res = resolver_problema_lineal("max", 1, 1, restricciones)
        self.assertEqual(res["status"], "multiple")

    def test_problema_inviable(self):
        """Detecta problemas sin región factible."""
        restricciones = [
            {"coef_x1": 1, "coef_x2": -1, "operador": ">=", "valor": 1},
            {"coef_x1": -1, "coef_x2": 1, "operador": ">=", "valor": 2},
        ]
        res = resolver_problema_lineal("max", 1, 1, restricciones)
        self.assertEqual(res["status"], "inviable")

from .sistema_lineal import resolver_sistema_pasos

class SistemaLinealTestCase(SimpleTestCase):
    def test_resolver_sistema(self):
        res = resolver_sistema_pasos('3 x1 + 5 x2 = 6', '4 x1 + 2 x2 = 5')
        self.assertAlmostEqual(res['resultado']['x1'], 13/14)
        self.assertAlmostEqual(res['resultado']['x2'], 9/14, places=1)
        self.assertIn('Punto de intersección', res['html'])
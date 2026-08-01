from manim import *

ELECTRON_COLOR = BLUE_C
WIRE_COLOR = WHITE
CURRENT_COLOR = YELLOW


class CircuitoKCL(Scene):
    def construct(self):
        # ---------- 0. Titulo ----------
        titulo = Text("Ley de Corrientes de Kirchhoff (LCK)", font_size=40, weight=BOLD)
        subtitulo = Text("Suma de corrientes que entran = suma de corrientes que salen",
                          font_size=24, color=GRAY_B)
        subtitulo.next_to(titulo, DOWN)
        self.play(Write(titulo))
        self.play(FadeIn(subtitulo, shift=UP))
        self.wait(1)
        self.play(FadeOut(titulo), FadeOut(subtitulo))

        # ================================================================
        # 1. GEOMETRIA EXPLICITA (todas las coordenadas se definen a mano,
        #    ningun punto de conexion se "inventa" con un offset arbitrario)
        # ================================================================
        BAT_X = -5
        NODE_A = np.array([-2, 2, 0])
        NODE_B = np.array([2, 2, 0])
        BAT_TOP = np.array([BAT_X, 2, 0])
        BAT_BOTTOM = np.array([BAT_X, -2, 0])

        R1_Y = 2.8
        R2_Y = 1.2
        R1_LEFT = np.array([-2, R1_Y, 0])
        R1_RIGHT = np.array([2, R1_Y, 0])
        R2_LEFT = np.array([-2, R2_Y, 0])
        R2_RIGHT = np.array([2, R2_Y, 0])

        # --- Bateria: simbolo + cables (leads) que llegan EXACTAMENTE a BAT_TOP/BAT_BOTTOM ---
        plate_larga = Line(UP * 0.35, DOWN * 0.35, stroke_width=6, color=WIRE_COLOR).move_to([BAT_X, 0.15, 0])
        plate_corta = Line(UP * 0.18, DOWN * 0.18, stroke_width=6, color=WIRE_COLOR).move_to([BAT_X, -0.15, 0])
        mas = Text("+", font_size=22, color=WIRE_COLOR).next_to(plate_larga, LEFT, buff=0.15)
        menos = Text("-", font_size=26, color=WIRE_COLOR).next_to(plate_corta, RIGHT, buff=0.15)
        lead_top = Line(plate_larga.get_top(), BAT_TOP, color=WIRE_COLOR)
        lead_bottom = Line(plate_corta.get_bottom(), BAT_BOTTOM, color=WIRE_COLOR)
        bateria = VGroup(lead_top, plate_larga, mas, plate_corta, menos, lead_bottom)

        # --- Resistores (zigzag), definidos entre dos puntos exactos ---
        r1 = self.crear_resistor(R1_LEFT, R1_RIGHT)
        r2 = self.crear_resistor(R2_LEFT, R2_RIGHT)
        r1_label = Text("R1", font_size=24).next_to(r1, UP, buff=0.15)
        r2_label = Text("R2", font_size=24).next_to(r2, DOWN, buff=0.15)

        # --- Cables (todos como Line entre puntos reales, sin arcos ni offsets) ---
        wire_bat_to_a = Line(BAT_TOP, NODE_A, color=WIRE_COLOR)
        wire_a_up = Line(NODE_A, R1_LEFT, color=WIRE_COLOR)
        wire_b_up = Line(R1_RIGHT, NODE_B, color=WIRE_COLOR)
        wire_a_down = Line(NODE_A, R2_LEFT, color=WIRE_COLOR)
        wire_b_down = Line(R2_RIGHT, NODE_B, color=WIRE_COLOR)
        CORNER_TR = np.array([5, 2, 0])
        CORNER_BR = np.array([5, -2, 0])
        wire_b_to_corner = Line(NODE_B, CORNER_TR, color=WIRE_COLOR)
        wire_right_side = Line(CORNER_TR, CORNER_BR, color=WIRE_COLOR)
        wire_bottom = Line(CORNER_BR, BAT_BOTTOM, color=WIRE_COLOR)

        nodo_a_dot = Dot(NODE_A, color=WIRE_COLOR, radius=0.06)
        nodo_b_dot = Dot(NODE_B, color=WIRE_COLOR, radius=0.06)
        label_a = Text("Nodo A", font_size=22, color=YELLOW).next_to(NODE_A, UP, buff=0.35)
        label_b = Text("Nodo B", font_size=22, color=YELLOW).next_to(NODE_B, UP, buff=0.35)

        circuito = VGroup(
            bateria, wire_bat_to_a,
            wire_a_up, r1, wire_b_up,
            wire_a_down, r2, wire_b_down,
            wire_b_to_corner, wire_right_side, wire_bottom,
            nodo_a_dot, nodo_b_dot,
        )
        circuito.move_to(ORIGIN).shift(DOWN * 0.3)

        # Como movimos el VGroup completo, recalculamos las coordenadas absolutas
        # reales de cada punto de interes leyendo la posicion final de cada objeto.
        BAT_TOP = lead_top.get_end()
        BAT_BOTTOM = lead_bottom.get_end()
        NODE_A = nodo_a_dot.get_center()
        NODE_B = nodo_b_dot.get_center()
        R1_LEFT_F, R1_RIGHT_F = r1.get_start(), r1.get_end()
        R2_LEFT_F, R2_RIGHT_F = r2.get_start(), r2.get_end()
        CORNER_TR = wire_right_side.get_start()
        CORNER_BR = wire_right_side.get_end()

        self.play(Create(circuito), run_time=2.5)
        self.play(FadeIn(label_a), FadeIn(label_b), FadeIn(r1_label), FadeIn(r2_label))
        self.wait(0.5)

        # ================================================================
        # 2. FLUJO DE ELECTRONES (recorren el lazo COMPLETO: bateria -> nodo A
        #    -> se dividen en R1/R2 -> nodo B -> vuelta por la derecha y abajo
        #    -> bateria). Esto es fisicamente correcto: el mismo electron que
        #    sale de un lado de la bateria recorre el circuito y regresa.
        # ================================================================
        info_electrones = Text(
            "Los electrones (-) fluyen del polo (-) al polo (+) de la bateria",
            font_size=24, color=ELECTRON_COLOR
        ).to_edge(DOWN)
        self.play(FadeIn(info_electrones))

        n_electrones = 6
        electrones = VGroup(*[
            Dot(radius=0.07, color=ELECTRON_COLOR).move_to(BAT_TOP + RIGHT * 0.01 * i)
            for i in range(n_electrones)
        ])
        self.play(FadeIn(electrones))

        # Fase 1: de la bateria al nodo A
        self.play(
            *[MoveAlongPath(e, Line(e.get_center(), NODE_A), rate_func=linear) for e in electrones],
            run_time=1.0,
        )

        # Fase 2: division en el nodo A -> mitad por R1, mitad por R2 -> reunion en nodo B
        mitad = n_electrones // 2
        anims_fase2 = []
        for i, e in enumerate(electrones):
            if i < mitad:
                pts = [NODE_A, R1_LEFT_F, R1_RIGHT_F, NODE_B]
            else:
                pts = [NODE_A, R2_LEFT_F, R2_RIGHT_F, NODE_B]
            path = VMobject()
            path.set_points_as_corners(pts)
            anims_fase2.append(MoveAlongPath(e, path, rate_func=linear))
        self.play(*anims_fase2, run_time=2.2)

        # Fase 3: de nodo B, por la derecha y abajo, de regreso a la bateria
        anims_fase3 = []
        for e in electrones:
            pts = [NODE_B, CORNER_TR, CORNER_BR, BAT_BOTTOM]
            path = VMobject()
            path.set_points_as_corners(pts)
            anims_fase3.append(MoveAlongPath(e, path, rate_func=linear))
        self.play(*anims_fase3, run_time=2.0)
        self.play(FadeOut(electrones), FadeOut(info_electrones))

        # ================================================================
        # 3. CORRIENTE CONVENCIONAL (sentido opuesto a los electrones)
        # ================================================================
        info_corriente = Text(
            "La corriente convencional (I) fluye en sentido opuesto: del (+) al (-)",
            font_size=24, color=CURRENT_COLOR
        ).to_edge(DOWN)
        self.play(FadeIn(info_corriente))

        flecha_I = Arrow(BAT_TOP + LEFT * 0.9, NODE_A, color=CURRENT_COLOR, buff=0.1)
        I_label = Text("I = 3 A", font_size=26, color=CURRENT_COLOR).next_to(flecha_I, UP, buff=0.1)

        flecha_I1 = Arrow(NODE_A + UP * 0.3, R1_LEFT_F, color=CURRENT_COLOR, buff=0.05)
        I1_label = Text("I1 = 1 A", font_size=24, color=CURRENT_COLOR).next_to(r1, UP, buff=0.55)

        flecha_I2 = Arrow(NODE_A + DOWN * 0.3, R2_LEFT_F, color=CURRENT_COLOR, buff=0.05)
        I2_label = Text("I2 = 2 A", font_size=24, color=CURRENT_COLOR).next_to(r2, DOWN, buff=0.55)

        self.play(GrowArrow(flecha_I), FadeIn(I_label))
        self.wait(0.3)
        self.play(GrowArrow(flecha_I1), FadeIn(I1_label), GrowArrow(flecha_I2), FadeIn(I2_label))
        self.wait(1)

        # ================================================================
        # 4. ECUACION DE KCL EN EL NODO A
        # ================================================================
        self.play(Circumscribe(nodo_a_dot, color=YELLOW, run_time=1.2))

        ecuacion = Text("I = I1 + I2", font_size=32, weight=BOLD).to_edge(UP)
        ecuacion_valores = Text("3 A = 1 A + 2 A", font_size=28, color=GREEN).next_to(ecuacion, DOWN)

        self.play(FadeOut(info_corriente))
        self.play(Write(ecuacion))
        self.play(Write(ecuacion_valores))
        self.wait(1)

        recuadro = SurroundingRectangle(VGroup(ecuacion, ecuacion_valores), color=GREEN, buff=0.25)
        self.play(Create(recuadro))
        self.wait(1.5)

        conclusion = Text(
            "En cualquier nodo, la suma de corrientes entrantes\n"
            "es igual a la suma de corrientes salientes.",
            font_size=26, color=GRAY_A
        ).to_edge(DOWN)
        self.play(
            FadeOut(circuito), FadeOut(label_a), FadeOut(label_b),
            FadeOut(r1_label), FadeOut(r2_label),
            FadeOut(flecha_I), FadeOut(I_label),
            FadeOut(flecha_I1), FadeOut(I1_label),
            FadeOut(flecha_I2), FadeOut(I2_label),
        )
        self.play(FadeIn(conclusion))
        self.wait(2)

    def crear_resistor(self, punto_izq, punto_der, alto=0.3, n_zigzag=6):
        """Resistor tipo zigzag dibujado exactamente entre dos puntos dados."""
        punto_izq = np.array(punto_izq, dtype=float)
        punto_der = np.array(punto_der, dtype=float)
        vector = punto_der - punto_izq
        largo = np.linalg.norm(vector)
        direccion = vector / largo
        normal = np.array([-direccion[1], direccion[0], 0])  # perpendicular

        puntos = [punto_izq]
        paso = largo / n_zigzag
        for i in range(1, n_zigzag):
            offset = alto / 2 if i % 2 == 1 else -alto / 2
            puntos.append(punto_izq + direccion * paso * i + normal * offset)
        puntos.append(punto_der)

        r = VMobject(color=WIRE_COLOR)
        r.set_points_as_corners(puntos)
        return r
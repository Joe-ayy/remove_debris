#!/usr/bin/env python


from gimpfu import *


# change this so that background colors are only saved once
def paint_over(drw, x, y, cart_size):
    brush_color = "white"
    temp_brush = "b1"
    center = [x, y]
    og_background = pdb.gimp_context_get_background()
    og_foreground = pdb.gimp_context_get_foreground()
    pdb.gimp_context_set_foreground(brush_color)
    temp_brush = pdb.gimp_brush_new(temp_brush)
    pdb.gimp_brush_set_shape(temp_brush, 0)
    pdb.gimp_brush_set_radius(temp_brush, 1000)
    pdb.gimp_context_set_brush_size(cart_size)
    pdb.gimp_brush_set_hardness(temp_brush, 100)
    pdb.gimp_context_set_opacity(100)
    pdb.gimp_pencil(drw, 2, center)
    pdb.gimp_context_set_background(og_background)
    pdb.gimp_context_set_foreground(og_foreground)
    pdb.gimp_brush_delete(temp_brush)


def run_script(img, drw):
    img = gimp.image_list()[0]
    draw = pdb.gimp_image_get_active_drawable(img)
    file_path = pdb.gimp_image_get_filename(gimp.image_list()[0])

    return


register(
    "remove_debris",
    "Remove debris, streaks, and bad data points from the map while retaining the integrity of the store layout.",
    "This plugin runs automatically upon execution. User defined number of passes may be added at a later time.",
    "Joey Harrison & Jair Pedroza",
    "J.H. & J.P.",
    "11/26",
    "<Image>/Tools/Transform Tools/_Remove Debris",
    "RGB*, GRAY*",
    [],
    [],
    run_script)

main()

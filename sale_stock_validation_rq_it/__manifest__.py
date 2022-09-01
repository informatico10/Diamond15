{
    'name': 'Sale Stock Validation Rq It',
    'version': '1.0',
    'description': """
        Se creará un aviso cuando se intente guardar una cotización,
        donde las cantidades solicitadas por el cliente,
        supere el stock disponible del producto; se permitirá guardar
        la cotización, pero no se podrá confirmar si no hay stock;
        en casos especiales que necesiten confirmar el pedido,
        y generar la factura así no cuenten con el stock, se realizaran 
        las siguientes adaptaciones: Crear el grupo,

        “Responsable Confirmación de Pedido de Venta Sin Stock”

        todos los que estén en este grupo, pueden aprobar las cotizaciones
        que contengan productos sin suficiente stock, bien sea para que
        puedan emitir la factura o hacer una entrega parcial.

        En la plantilla de la cotización se habilitará el botón
        “Solicitar Confirmación” visible para el vendedor, cuando uno de
        los productos a cotizar no cuente con el stock suficiente.
        (*) Se creará la “Notificación Confirmación de Pedido de Venta Sin Stock”,
        para informar a los “Responsables Confirmación de Pedido de Venta Sin Stock”,
        que el pedido está pendiente de aprobación y en la plantilla de
        la cotización se habilitará el botón “Confirmar Pedido” exclusivo para ellos. (*)
    """,
    'author': 'ITGRUPO',
    'license': 'LGPL-3',
    'category': 'stock picking',
    'auto_install': False,
    'depends': [
        'sale',
        'product',
        'category_only_rq_it'
    ],
    'data': [
        # 'security/security.xml',
        'views/views.xml',
    ],
    'installable': True
}
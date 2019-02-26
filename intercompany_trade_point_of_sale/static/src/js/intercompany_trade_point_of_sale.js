/*
    Copyright (C) 2014 - Today: GRAP (http://www.grap.coop)
    @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

/* global openerp */

'use strict'

openerp.intercompany_trade_point_of_sale = function (instance) {
  var module = instance.point_of_sale

  // We can't extend it because self.pos not ready yet
  var _initializePosModel_ = module.PosModel.prototype.initialize
  module.PosModel.prototype.initialize = function (session, attributes) {
    // Override domain for res.partner to limit customers loaded
    this.models.some(function (m) {
      if (m.model !== 'res.partner') {
        return false
      }
      // Check if not already done by someone else
      for (var i = 0; i < m.domain.length; i++) {
        var domainTuple = m.domain[i]
        if (domainTuple[0] === 'intercompany_trade') {
          return true
        }
      }
      m.domain.push(['intercompany_trade', '=', false])
      return true
    })
    return _initializePosModel_.call(this, session, attributes)
  }
}

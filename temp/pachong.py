# -*- coding:utf8 -*-
import os, sys, re, json
import argparse
from copy import deepcopy
from copy import deepcopy
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import vthread
import pymongo
from copy import deepcopy

html_text = '''
<div id="main-content" class="region clearfix">
        <div class="region region-content">
    <div id="block-system-main" class="block block-system clearfix">

    
  <div class="content">
    <div id="node-129" class="node node-hegre-model clearfix" about="/models/alena" typeof="sioc:Item foaf:Document">

    
        
      <span property="dc:title" content="Alena" class="rdf-meta element-hidden"/><span property="sioc:num_replies" content="0" datatype="xsd:integer" class="rdf-meta element-hidden"/>    
  <div class="content">
    <div class="field-name-model-board field-type-image"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/w780/public/models/alena-980x553.jpg?itok=S_fTVegN" width="780" height="440"/></div><div class="grid-5 alpha hegre-model-profile"><div class="box border"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/small-portrait/public/models/alena-148.jpg?itok=zaiXCeCv" width="124" height="161"/><h4>Profile</h4><div class="item-list"><ul><li class="first">Height: 5' 6" (169 cm)</li>
<li>Weight: 112 lbs (51 kg)</li>
<li>Age: 21</li>
<li>Occupation: Student</li>
<li class="last">Country: <a href="/models/country/ukraine" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">Ukraine</a></li>
</ul></div></div></div><div class="grid-15 omega"><h2>New and Fearless</h2><div class="field-name-body field-type-text-with-summary"><p><strong>Alena knows that being a model isn’t just about having the right look; it’s also about walking the right walk.</strong></p>
<p>Perhaps not the most stunning model on Hegre-Art.com; Alena certainly knows how to compensate with loads of sensuality and body language that reads like an erotic thriller you only bring out when alone and tucked under the covers.  At first she comes off as innocent, but deep down she has the heart of a fearless vixen.</p>
<p>Alena smiles easy and prides herself on her easy going personality.  She grew up under the open skies of the countryside but now lives in the big city and studies computer landscaping full time.  She loves her perky breasts and admits with a smile that they have taken her far in life.</p>
<p><em><strong>Alena is brand new to the modeling business and we certainly hope she decides to stick around!</strong></em></p>
</div><div class="grid-11 model-join alpha omega"><div class="box"><h3>Alena: Complete and Uncensored</h3><p>Access <em>every</em> photo and film of <strong>Alena</strong>, including:</p><div class="item-list"><ul class="model-stats"><li class="first last"><em class="placeholder">590 MB</em>+ of zip archives with over <em class="placeholder">270</em> photos</li>
</ul></div><p>Plus access to the entire Hegre-Art library of 248,291 photos and over 481 films.</p><a href="http://nudes.hegre-art.com/hit/1/5/108914/17/2142" class="hegre-direct"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/all/themes/hegregirls/images/get-full-access.png" alt=""/></a></div></div></div><div class="clearfix"/><h3>Alena Galleries</h3><div id="node-1670" class="grid-4 alpha node-grid " about="/galleries/alena-alone" typeof="sioc:Item foaf:Document">

    
        <span property="dc:title" content="Alena Alone" class="rdf-meta element-hidden"/><span property="sioc:num_replies" content="0" datatype="xsd:integer" class="rdf-meta element-hidden"/>    
  <div class="content">
    <div class="field-name-coverl field-type-image"><a href="/galleries/alena-alone" rel="http://www.hegregirls.com/sites/default/files/styles/popup/public/covers/AlenaAlone-coverl.jpg?itok=MVRnUVy2"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/thumbnail/public/covers/AlenaAlone-coverl.jpg?itok=j_T6wIir" alt="" title="Alena Alone"/></a></div><div class="release-date">June 21<sup>st</sup>, 2007</div><div class="preview-link"><a href="/free-nudes/hegre-art-alena-alone">Preview Alena Alone</a></div>  </div>
    <div class="grid-meta">
    <h4><a href="/galleries/alena-alone">Alena Alone</a></h4>
      </div>
      <div class="clearfix margin-top">
      </div>
    
</div>
<div id="node-1614" class="grid-4  node-grid " about="/galleries/alena-coke" typeof="sioc:Item foaf:Document">

    
        <span property="dc:title" content="Alena Coke" class="rdf-meta element-hidden"/><span property="sioc:num_replies" content="0" datatype="xsd:integer" class="rdf-meta element-hidden"/>    
  <div class="content">
    <div class="field-name-coverl field-type-image"><a href="/galleries/alena-coke" rel="http://www.hegregirls.com/sites/default/files/styles/popup/public/covers/AlenaCocaCola-coverl.jpg?itok=UaoFZSE_"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/thumbnail/public/covers/AlenaCocaCola-coverl.jpg?itok=Gm9_9bBk" alt="" title="Alena Coke"/></a></div><div class="release-date">April 25<sup>th</sup>, 2007</div><div class="preview-link"><a href="/free-nudes/hegre-art-alena-coke">Preview Alena Coke</a></div>  </div>
    <div class="grid-meta">
    <h4><a href="/galleries/alena-coke">Alena Coke</a></h4>
      </div>
      <div class="clearfix margin-top">
      </div>
    
</div>
<div id="node-3431" class="grid-4  node-grid " about="/galleries/alena-hot-bath" typeof="sioc:Item foaf:Document">

    
        <span property="dc:title" content="Alena Hot Bath" class="rdf-meta element-hidden"/><span property="sioc:num_replies" content="0" datatype="xsd:integer" class="rdf-meta element-hidden"/>    
  <div class="content">
    <div class="field-name-coverl field-type-image"><a href="/galleries/alena-hot-bath" rel="http://www.hegregirls.com/sites/default/files/styles/popup/public/covers/AlenaHotBath-coverl.jpg?itok=gCNrUgJY"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/thumbnail/public/covers/AlenaHotBath-coverl.jpg?itok=4V4DeO0s" alt="" title="Alena Hot Bath"/></a></div><div class="release-date">December 11<sup>th</sup>, 2006</div>  </div>
    <div class="grid-meta">
    <h4><a href="/galleries/alena-hot-bath">Alena Hot Bath</a></h4>
      </div>
      <div class="clearfix margin-top">
      </div>
    
</div>
<div id="node-1476" class="grid-4  node-grid " about="/galleries/alena-kitchen-setting" typeof="sioc:Item foaf:Document">

    
        <span property="dc:title" content="Alena Kitchen Setting" class="rdf-meta element-hidden"/><span property="sioc:num_replies" content="0" datatype="xsd:integer" class="rdf-meta element-hidden"/>    
  <div class="content">
    <div class="field-name-coverl field-type-image"><a href="/galleries/alena-kitchen-setting" rel="http://www.hegregirls.com/sites/default/files/styles/popup/public/covers/AlenaKitchenSetting-coverl.jpg?itok=dR1M8tWG"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/thumbnail/public/covers/AlenaKitchenSetting-coverl.jpg?itok=IUDLs45e" alt="" title="Alena Kitchen Setting"/></a></div><div class="release-date">November 6<sup>th</sup>, 2006</div><div class="preview-link"><a href="/free-nudes/hegre-art-alena-kitchen-setting">Preview Alena Kitchen Setting</a></div>  </div>
    <div class="grid-meta">
    <h4><a href="/galleries/alena-kitchen-setting">Alena Kitchen Setting</a></h4>
      </div>
      <div class="clearfix margin-top">
      </div>
    
</div>
<div id="node-1409" class="grid-4 omega node-grid " about="/galleries/alena-skin-skin" typeof="sioc:Item foaf:Document">

    
        <span property="dc:title" content="Alena Skin To Skin" class="rdf-meta element-hidden"/><span property="sioc:num_replies" content="0" datatype="xsd:integer" class="rdf-meta element-hidden"/>    
  <div class="content">
    <div class="field-name-coverl field-type-image"><a href="/galleries/alena-skin-skin" rel="http://www.hegregirls.com/sites/default/files/styles/popup/public/covers/AlenaSkinToSkin-coverl.jpg?itok=zLZOMQzO"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/thumbnail/public/covers/AlenaSkinToSkin-coverl.jpg?itok=5cujcdJP" alt="" title="Alena Skin To Skin"/></a></div><div class="release-date">August 28<sup>th</sup>, 2006</div><div class="preview-link"><a href="/free-nudes/hegre-art-alena-leather-dreams">Preview Alena Skin To Skin</a></div>  </div>
    <div class="grid-meta">
    <h4><a href="/galleries/alena-skin-skin">Alena Skin To Skin</a></h4>
      </div>
      <div class="clearfix margin-top">
      </div>
    
</div>
<div id="node-1320" class="grid-4 alpha node-grid " about="/galleries/alena-table-dance" typeof="sioc:Item foaf:Document">

    
        <span property="dc:title" content="Alena Table Dance" class="rdf-meta element-hidden"/><span property="sioc:num_replies" content="0" datatype="xsd:integer" class="rdf-meta element-hidden"/>    
  <div class="content">
    <div class="field-name-coverl field-type-image"><a href="/galleries/alena-table-dance" rel="http://www.hegregirls.com/sites/default/files/styles/popup/public/covers/AlenaTableDance-coverl.jpg?itok=gz_ImJ2S"><img typeof="foaf:Image" src="http://www.hegregirls.com/sites/default/files/styles/thumbnail/public/covers/AlenaTableDance-coverl.jpg?itok=k3Bp_3GB" alt="" title="Alena Table Dance"/></a></div><div class="release-date">May 29<sup>th</sup>, 2006</div><div class="preview-link"><a href="/free-nudes/hegre-art-alena-table-dance">Preview Alena Table Dance</a></div>  </div>
    <div class="grid-meta">
    <h4><a href="/galleries/alena-table-dance">Alena Table Dance</a></h4>
      </div>
      <div class="clearfix margin-top">
      </div>
    
</div>
<div class="clearfix bottom-border"/>  </div>
      <div class="clearfix margin-top">
      </div>
    
</div>
  </div>
</div>
<div id="block-hegre-hegre-join-banner" class="block block-hegre">

    
  <div class="content">
    <div class="clearfix"><div class="image"><a href="http://nudes.hegre-art.com/hit/1/5/108914/17/2142" class="hegre-direct"><img typeof="foaf:Image" src="http://hegregirls.com/sites/all/themes/hegregirls/images/bottom-join-banner.jpg" alt=""/></a></div><div class="meta"><div class="item-list"><ul><li class="first">248,291 Photos</li>
<li class="last">481 Films</li>
</ul></div></div></div>  </div>
</div>
  </div>
    </div>
'''

b = pq(html_text, parser='html')
print(b('.content .content .grid-4 .preview-link'))